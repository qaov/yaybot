"""
MIT License

Copyright (c) 2023 qvco

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import re
import json
from datetime import datetime

from .. import client
from ..config import Configs, Endpoints
from ..errors import ForbiddenError, NotFoundError
from ..models import ConferenceCall, Post, SharedUrl, Survey
from ..responses import (
    BookmarkPostResponse,
    CreatePostResponse,
    PostResponse,
    PostsResponse,
    PostLikersResponse,
    PostTagsResponse,
    LikePostsResponse,
    ValidationPostResponse,
)
from ..utils import build_message_tags


class PostAPI(object):
    def __init__(self, base: client.BaseClient) -> None:
        self.__base = base

    def add_bookmark(self, user_id: int, post_id: int) -> BookmarkPostResponse:
        return self.__base._request(
            "PUT",
            endpoint=f"{Endpoints.USERS_V1}/{user_id}/bookmarks/{post_id}",
            data_type=BookmarkPostResponse,
        )

    def add_group_highlight_post(self, group_id: int, post_id: int):
        """

        投稿をグループのまとめに追加します

        """
        return self.__base._request(
            "PUT",
            endpoint=f"{Endpoints.GROUPS_V1}/{group_id}/highlights/{post_id}",
        )

    def create_call_post(
        self,
        text: str = None,
        font_size: int = None,
        color: int = None,
        group_id: int = None,
        call_type: str = None,
        category_id: int = None,
        game_title: str = None,
        joinable_by: str = None,
        message_tags: list = [],
        attachment_filename: str = None,
        attachment_2_filename: str = None,
        attachment_3_filename: str = None,
        attachment_4_filename: str = None,
        attachment_5_filename: str = None,
        attachment_6_filename: str = None,
        attachment_7_filename: str = None,
        attachment_8_filename: str = None,
        attachment_9_filename: str = None,
    ) -> ConferenceCall:
        text, message_tags = build_message_tags(text)

        timestamp = int(datetime.now().timestamp())

        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V2}/new_conference_call",
            payload={
                "text": text,
                "font_size": font_size,
                "color": color,
                "group_id": group_id,
                "call_type": call_type,
                "uuid": self.__base.uuid,
                "api_key": Configs.API_KEY,
                "timestamp": timestamp,
                "signed_info": self.generate_signed_info(
                    self.__base.device_uuid, timestamp
                ),
                "category_id": category_id,
                "game_title": game_title,
                "joinable_by": joinable_by,
                "message_tags": message_tags,
                "attachment_filename": attachment_filename,
                "attachment_2_filename": attachment_2_filename,
                "attachment_3_filename": attachment_3_filename,
                "attachment_4_filename": attachment_4_filename,
                "attachment_5_filename": attachment_5_filename,
                "attachment_6_filename": attachment_6_filename,
                "attachment_7_filename": attachment_7_filename,
                "attachment_8_filename": attachment_8_filename,
                "attachment_9_filename": attachment_9_filename,
            },
            data_type=CreatePostResponse,
        ).conference_call

    def create_group_pin_post(self, post_id: int, group_id: int):
        return self.__base._request(
            "PUT",
            endpoint=f"{Endpoints.POSTS_V2}/group_pinned_post",
            payload={"post_id": post_id, "group_id": group_id},
        )

    def create_pin_post(self, post_id: int):
        return self.__base._request(
            "POST", endpoint=f"{Endpoints.PINNED_V1}/posts", payload={"id": post_id}
        )

    def create_post(
        self,
        text: str = None,
        font_size: int = 0,
        color: int = 0,
        in_reply_to: int = None,
        group_id: int = None,
        mention_ids: list[int] = None,
        choices: list[str] = None,
        shared_url: str = None,
        message_tags: list = [],
        attachment_filename: str = None,
        attachment_2_filename: str = None,
        attachment_3_filename: str = None,
        attachment_4_filename: str = None,
        attachment_5_filename: str = None,
        attachment_6_filename: str = None,
        attachment_7_filename: str = None,
        attachment_8_filename: str = None,
        attachment_9_filename: str = None,
        video_file_name: str = None,
    ) -> Post:
        text, message_tags = build_message_tags(text)

        post_type = (
            "survey"
            if choices
            else "shareable_url"
            if shared_url
            else "video"
            if video_file_name
            else "image"
            if attachment_filename
            else "text"
        )

        if shared_url is not None:
            try:
                shared_url = self.get_url_metadata(url=shared_url).data
            except ForbiddenError:
                self.__base.logger.error("Unable to get the URL metadata.")
                shared_url = None

        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V3}/new",
            payload={
                "text": text,
                "font_size": font_size,
                "color": color,
                "in_reply_to": in_reply_to,
                "group_id": group_id,
                "post_type": post_type,
                "mention_ids": mention_ids,
                "choices": choices,
                "shared_url": shared_url,
                "message_tags": message_tags,
                "attachment_filename": attachment_filename,
                "attachment_2_filename": attachment_2_filename,
                "attachment_3_filename": attachment_3_filename,
                "attachment_4_filename": attachment_4_filename,
                "attachment_5_filename": attachment_5_filename,
                "attachment_6_filename": attachment_6_filename,
                "attachment_7_filename": attachment_7_filename,
                "attachment_8_filename": attachment_8_filename,
                "attachment_9_filename": attachment_9_filename,
                "video_file_name": video_file_name,
            },
            data_type=Post,
            jwt_required=True,
        )

    def create_repost(
        self,
        post_id: int,
        text: str = None,
        font_size: int = None,
        color: int = None,
        in_reply_to: int = None,
        group_id: int = None,
        mention_ids: list[int] = None,
        choices: list[str] = None,
        shared_url: dict[str, str | int] = None,
        message_tags: list = [],
        attachment_filename: str = None,
        attachment_2_filename: str = None,
        attachment_3_filename: str = None,
        attachment_4_filename: str = None,
        attachment_5_filename: str = None,
        attachment_6_filename: str = None,
        attachment_7_filename: str = None,
        attachment_8_filename: str = None,
        attachment_9_filename: str = None,
        video_file_name: str = None,
    ) -> Post:
        text, message_tags = build_message_tags(text)

        post_type = (
            "survey"
            if choices
            else "shareable_url"
            if shared_url
            else "video"
            if video_file_name
            else "image"
            if attachment_filename
            else "text"
        )

        if shared_url is not None:
            try:
                shared_url = self.get_url_metadata(url=shared_url).data
            except ForbiddenError:
                self.__base.logger.error("Unable to get the URL metadata.")
                shared_url = None

        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V3}/repost",
            payload={
                "post_id": post_id,
                "text": text,
                "font_size": font_size,
                "color": color,
                "in_reply_to": in_reply_to,
                "group_id": group_id,
                "post_type": post_type,
                "mention_ids": mention_ids,
                "choices": choices,
                "shared_url": shared_url,
                "message_tags": message_tags,
                "attachment_filename": attachment_filename,
                "attachment_2_filename": attachment_2_filename,
                "attachment_3_filename": attachment_3_filename,
                "attachment_4_filename": attachment_4_filename,
                "attachment_5_filename": attachment_5_filename,
                "attachment_6_filename": attachment_6_filename,
                "attachment_7_filename": attachment_7_filename,
                "attachment_8_filename": attachment_8_filename,
                "attachment_9_filename": attachment_9_filename,
                "video_file_name": video_file_name,
            },
            data_type=CreatePostResponse,
            jwt_required=True,
        ).post

    def create_share_post(
        self,
        shareable_type: str,
        shareable_id: int,
        text: str = None,
        font_size: int = None,
        color: int = None,
        group_id: int = None,
    ) -> Post:
        timestamp = int(datetime.now().timestamp())

        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V2}/new_share_post",
            payload={
                "shareable_type": shareable_type,
                "shareable_id": shareable_id,
                "text": text,
                "font_size": font_size,
                "color": color,
                "group_id": group_id,
                "uuid": self.__base.uuid,
                "api_key": Configs.API_KEY,
                "timestamp": timestamp,
                "signed_info": self.generate_signed_info(
                    self.__base.device_uuid, timestamp
                ),
            },
            data_type=Post,
        )

    def create_thread_post(
        self,
        post_id: int,
        text: str = None,
        font_size: int = None,
        color: int = None,
        in_reply_to: int = None,
        group_id: int = None,
        mention_ids: list[int] = None,
        choices: list[str] = None,
        shared_url: dict[str, str | int] = None,
        message_tags: list = [],
        attachment_filename: str = None,
        attachment_2_filename: str = None,
        attachment_3_filename: str = None,
        attachment_4_filename: str = None,
        attachment_5_filename: str = None,
        attachment_6_filename: str = None,
        attachment_7_filename: str = None,
        attachment_8_filename: str = None,
        attachment_9_filename: str = None,
        video_file_name: str = None,
    ) -> Post:
        text, message_tags = build_message_tags(text)

        post_type = (
            "survey"
            if choices
            else "shareable_url"
            if shared_url
            else "video"
            if video_file_name
            else "image"
            if attachment_filename
            else "text"
        )

        if shared_url is not None:
            try:
                shared_url = self.get_url_metadata(url=shared_url).data
            except ForbiddenError:
                self.__base.logger.error("Unable to get the URL metadata.")
                shared_url = None

        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.THREADS_V1}/{post_id}/posts",
            payload={
                "id": post_id,
                "text": text,
                "font_size": font_size,
                "color": color,
                "in_reply_to": in_reply_to,
                "group_id": group_id,
                "post_type": post_type,
                "mention_ids": mention_ids,
                "choices": choices,
                "shared_url": shared_url,
                "message_tags": message_tags,
                "attachment_filename": attachment_filename,
                "attachment_2_filename": attachment_2_filename,
                "attachment_3_filename": attachment_3_filename,
                "attachment_4_filename": attachment_4_filename,
                "attachment_5_filename": attachment_5_filename,
                "attachment_6_filename": attachment_6_filename,
                "attachment_7_filename": attachment_7_filename,
                "attachment_8_filename": attachment_8_filename,
                "attachment_9_filename": attachment_9_filename,
                "video_file_name": video_file_name,
            },
            data_type=Post,
            jwt_required=True,
        )

    def delete_all_post(self):
        try:
            return self.__base._request(
                "POST", endpoint=f"{Endpoints.POSTS_V1}/delete_all_post"
            )
        except NotFoundError:
            self.__base.logger.info("Post not found. Skipping...")

    def delete_group_pin_post(self, group_id: int):
        return self.__base._request(
            "DELETE",
            endpoint=f"{Endpoints.POSTS_V2}/group_pinned_post",
            payload={"group_id": group_id},
        )

    def delete_pin_post(self, post_id: int):
        return self.__base._request(
            "DELETE", endpoint=f"{Endpoints.PINNED_V1}/posts/{post_id}"
        )

    def get_bookmark(self, user_id: int, from_str: str = None) -> PostsResponse:
        params = {}
        if from_str:
            params = {"from": from_str}
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.USERS_V1}/{user_id}/bookmarks",
            params=params,
            data_type=PostsResponse,
        )

    def get_timeline_calls(self, **params) -> PostsResponse:
        """

        Parameters:
        ----------

            - group_id: int = None
            - from_timestamp: int = None
            - number: int = None
            - category_id: int = None
            - call_type: str = "voice"
            - include_circle_call: bool = None
            - cross_generation: bool = None
            - exclude_recent_gomimushi: bool = None
            - shared_interest_categories: bool = None

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/call_timeline",
            params=params,
            data_type=PostsResponse,
        )

    def get_conversation(self, conversation_id: int, **params) -> PostsResponse:
        """

        Parameters:
        ----------

            - conversation_id: int
            - group_id: int = None
            - thread_id: int = None
            - from_post_id: int = None
            - number: int = 50
            - reverse: bool = True

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.CONVERSATIONS_V2}/{conversation_id}",
            params=params,
            data_type=PostsResponse,
        )

    def get_conversation_root_posts(self, post_ids: list[int]) -> PostsResponse:
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.CONVERSATIONS_V2}/root_posts",
            params={"ids[]": post_ids},
            data_type=PostsResponse,
        )

    def get_following_call_timeline(self, **params) -> PostsResponse:
        """

        Parameters:
        ----------

            - from_timestamp: int = None
            - number: int = None
            - category_id: int = None
            - call_type: str = None
            - include_circle_call: bool = None
            - exclude_recent_gomimushi: bool = None

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/call_followers_timeline",
            params=params,
            data_type=PostsResponse,
        )

    def get_following_timeline(self, **params) -> PostsResponse:
        """

        Parameters:
        ----------

            - from_str: str = None
            - only_root: bool = None
            - order_by: str = None
            - number: int = None
            - mxn: int = None
            - reduce_selfie: bool = None
            - custom_generation_range: bool = None

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/following_timeline",
            params=params,
            data_type=PostsResponse,
        )

    def get_group_highlight_posts(self, group_id: int, **params) -> PostsResponse:
        """

        グループのまとめ投稿を取得します

        Parameters:
        ----------

            - group_id: int
            - from_post: int = None
            - number: int = None

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.GROUPS_V1}/{group_id}/highlights",
            params=params,
            data_type=PostsResponse,
        )

    def get_group_timeline_by_keyword(
        self, group_id: int, keyword: str, **params
    ) -> PostsResponse:
        """

        Parameters:
        ----------

            - group_id: int
            - keyword: str
            - from_post_id: int = None
            - number: int = None
            - only_thread_posts: bool = False

        """
        params["keyword"] = keyword
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.GROUPS_V2}/{group_id}/posts/search",
            params=params,
            data_type=PostsResponse,
        )

    def get_group_timeline(self, group_id: int, **params) -> PostsResponse:
        """

        Parameters:
        ----------

            - group_id: int
            - from_post_id: int
            - reverse: bool
            - post_type: str
            - number: int
            - only_root: bool

        """
        params["group_id"] = group_id
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/group_timeline",
            params=params,
            data_type=PostsResponse,
        )

    def get_timeline_by_hashtag(self, hashtag: str, **params) -> PostsResponse:
        """

        Parameters:
        ----------

            - hashtag: str - (required)
            - from_post_id: int - (optional)
            - number: int - (optional)

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/tags/{hashtag}",
            params=params,
            data_type=PostsResponse,
        )

    def get_my_posts(self, **params) -> PostsResponse:
        """

        Parameters:
        ---------------

            - from_post_id: int - (optional)
            - number: int - (optional)
            - include_group_post: bool - (optional)

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/mine",
            params=params,
            data_type=PostsResponse,
        )

    def get_post(self, post_id: int) -> Post:
        return self.__base._request(
            "GET", endpoint=f"{Endpoints.POSTS_V2}/{post_id}", data_type=PostResponse
        ).post

    def get_post_likers(self, post_id: int, **params) -> PostLikersResponse:
        """

        Parameters:
        ---------------

            - from_id: int - (optional)
            - number: int - (optional)

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V1}/{post_id}/likers",
            params=params,
            data_type=PostLikersResponse,
        )

    def get_post_reposts(self, post_id: int, **params: int) -> PostsResponse:
        """

        Parameters:
        ---------------

            - post_id: int - (required)
            - from_post_id: int - (optional)
            - number: int - (optional)

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/{post_id}/reposts",
            params=params,
            data_type=PostsResponse,
        )

    def get_posts(self, post_ids: list[int]) -> PostsResponse:
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/multiple",
            params={"post_ids[]": post_ids},
            data_type=PostsResponse,
        )

    def get_recommended_post_tags(
        self, tag: str = None, save_recent_search: bool = False
    ) -> PostTagsResponse:
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V1}/recommended_tag",
            payload={"tag": tag, "save_recent_search": save_recent_search},
            data_type=PostTagsResponse,
        )

    def get_recommended_posts(self, **params) -> PostsResponse:
        """

        Parameters:
        ---------------

            - experiment_num: int - (Required)
            - variant_num: int - (Required)
            - number: int - (Optional)

        """
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/recommended_timeline",
            params=params,
            data_type=PostsResponse,
        )

    def get_timeline_by_keyword(self, keyword: str = None, **params) -> PostsResponse:
        """

        Parameters:
        ---------------

            - keyword: str
            - from_post_id: int
            - number: int

        """
        params["keyword"] = keyword
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/search",
            params=params,
            data_type=PostsResponse,
        )

    def get_timeline(self, **params: int | str | bool) -> PostsResponse:
        # - from: str - (optional)
        """

        Parameters:
        ---------------

            - noreply_mode: bool - (optional)
            - from_post_id: int - (optional)
            - number: int - (optional)
            - order_by: str - (optional)
            - experiment_older_age_rules: bool - (optional)
            - shared_interest_categories: bool - (optional)
            - mxn: int - (optional)
            - en: int - (optional)
            - vn: int - (optional)
            - reduce_selfie: bool - (optional)
            - custom_generation_range: bool - (optional)

        """
        endpoint = f"{Endpoints.POSTS_V2}/timeline"
        if "noreply_mode" in params and params["noreply_mode"] is True:
            endpoint = f"{Endpoints.POSTS_V2}/noreply_timeline"
        return self.__base._request(
            "GET", endpoint=endpoint, params=params, data_type=PostsResponse
        )

    def get_url_metadata(self, url: str) -> SharedUrl:
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/url_metadata",
            params={"url": url},
            data_type=SharedUrl,
        )

    def get_user_timeline(self, user_id: int, **params) -> PostsResponse:
        """

        Parameters:
        ---------------

            - from_post_id: int - (optional)
            - number: int - (optional)
            - post_type: str - (optional)

        """
        params["user_id"] = user_id
        return self.__base._request(
            "GET",
            endpoint=f"{Endpoints.POSTS_V2}/user_timeline",
            params=params,
            data_type=PostsResponse,
        )

    def like_posts(self, post_ids: list[int]) -> LikePostsResponse:
        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V2}/like",
            payload={"post_ids": post_ids},
            data_type=LikePostsResponse,
        )

    def remove_bookmark(self, user_id: int, post_id: int):
        return self.__base._request(
            "DELETE",
            endpoint=f"{Endpoints.USERS_V1}/{user_id}/bookmarks/{post_id}",
        )

    def remove_group_highlight_post(self, group_id: int, post_id: int):
        return self.__base._request(
            "DELETE",
            endpoint=f"{Endpoints.GROUPS_V1}/{group_id}/highlights/{post_id}",
        )

    def remove_posts(self, post_ids: list[int]):
        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V2}/mass_destroy",
            payload={"posts_ids": post_ids},
        )

    def report_post(
        self,
        post_id: int,
        opponent_id: int,
        category_id: int,
        reason: str = None,
        screenshot_filename: str = None,
        screenshot_2_filename: str = None,
        screenshot_3_filename: str = None,
        screenshot_4_filename: str = None,
    ):
        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V3}/{post_id}/report",
            payload={
                "opponent_id": opponent_id,
                "category_id": category_id,
                "reason": reason,
                "screenshot_filename": screenshot_filename,
                "screenshot_2_filename": screenshot_2_filename,
                "screenshot_3_filename": screenshot_3_filename,
                "screenshot_4_filename": screenshot_4_filename,
            },
        )

    def unlike_post(self, post_id: int):
        return self.__base._request(
            "POST", endpoint=f"{Endpoints.POSTS_V1}/{post_id}/unlike"
        )

    def update_post(
        self,
        post_id: int,
        text: str = None,
        font_size: int = None,
        color: int = None,
        message_tags: list = [],
    ) -> Post:
        text, message_tags = build_message_tags(text)

        timestamp = int(datetime.now().timestamp())

        return self.__base._request(
            "PUT",
            endpoint=f"{Endpoints.POSTS_V3}/{post_id}",
            payload={
                "text": text,
                "font_size": font_size,
                "color": color,
                "message_tags": message_tags,
                "api_key": Configs.API_KEY,
                "timestamp": timestamp,
                "signed_info": self.generate_signed_info(
                    self.__base.device_uuid, timestamp
                ),
            },
        )

    def view_video(self, video_id: int):
        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.POSTS_V1}/videos/{video_id}/view",
        )

    def vote_survey(self, survey_id: int, choice_id: int) -> Survey:
        return self.__base._request(
            "POST",
            endpoint=f"{Endpoints.SURVEYS_V2}/{survey_id}/vote",
            payload={"choice_id": choice_id},
            data_type=ValidationPostResponse,
        ).survey
