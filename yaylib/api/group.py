"""
MIT License

Copyright (c) 2023 ekkx

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

from datetime import datetime

from .. import config
from ..models import CreateGroupQuota
from ..responses import (
    CreateGroupResponse,
    GroupCategoriesResponse,
    GroupResponse,
    GroupsRelatedResponse,
    GroupsResponse,
    GroupUserResponse,
    GroupUsersResponse,
    UnreadStatusResponse,
    UsersByTimestampResponse,
    UsersResponse,
)
from ..utils import md5


class GroupApi:
    """サークル API"""

    def __init__(self, client) -> None:
        from ..client import Client  # pylint: disable=import-outside-toplevel

        self.__client: Client = client

    async def accept_moderator_offer(self, group_id: int):
        return await self.__client.request(
            "PUT",
            config.API_HOST + f"/v1/groups/{group_id}/deputize",
        )

    async def accept_ownership_offer(
        self,
        group_id: int,
    ):
        return await self.__client.request(
            "PUT",
            config.API_HOST + f"/v1/groups/{group_id}/transfer",
        )

    async def accept_group_join_request(
        self,
        group_id: int,
        user_id: int,
    ):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/accept/{user_id}",
        )

    async def add_related_groups(self, group_id: int, related_group_id: list[int]):
        """

        関連サークルを追加する

        """
        return await self.__client.request(
            "PUT",
            config.API_HOST + f"/v1/groups/{group_id}/related",
            params={"related_group_id": related_group_id},
        )

    async def ban_group_user(self, group_id: int, user_id: int):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/ban/{user_id}",
        )

    async def check_group_unread_status(self, from_time: int = None) -> UnreadStatusResponse:
        params = {}
        if from_time:
            params["from_time"] = from_time
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v1/groups/unread_status",
            params=params,
            return_type=UnreadStatusResponse,
        )

    async def create_group(
        self,
        topic: str,
        description: str = None,
        secret: bool = None,
        hide_reported_posts: bool = None,
        hide_conference_call: bool = None,
        is_private: bool = None,
        only_verified_age: bool = None,
        only_mobile_verified: bool = None,
        call_timeline_display: bool = None,
        allow_ownership_transfer: bool = None,
        allow_thread_creation_by: str = None,
        gender: int = None,
        generation_groups_limit: int = None,
        group_category_id: int = None,
        cover_image_filename: str = None,
        sub_category_id: str = None,
        hide_from_game_eight: bool = None,
        allow_members_to_post_media: bool = None,
        allow_members_to_post_url: bool = None,
        guidelines: str = None,
    ) -> CreateGroupResponse:
        return await self.__client.request(
            "POST",
            config.API_HOST + "/v3/groups/new",
            json={
                "topic": topic,
                "description": description,
                "secret": secret,
                "hide_reported_posts": hide_reported_posts,
                "hide_conference_call": hide_conference_call,
                "is_private": is_private,
                "only_verified_age": only_verified_age,
                "only_mobile_verified": only_mobile_verified,
                "call_timeline_display": call_timeline_display,
                "allow_ownership_transfer": allow_ownership_transfer,
                "allow_thread_creation_by": allow_thread_creation_by,
                "gender": gender,
                "generation_groups_limit": generation_groups_limit,
                "group_category_id": group_category_id,
                "cover_image_filename": cover_image_filename,
                "uuid": self.__client.device_uuid,
                "api_key": config.API_KEY,
                "timestamp": int(datetime.now().timestamp()),
                "signed_info": md5(
                    self.__client.device_uuid, int(datetime.now().timestamp()), True
                ),
                "sub_category_id": sub_category_id,
                "hide_from_game_eight": hide_from_game_eight,
                "allow_members_to_post_image_and_video": allow_members_to_post_media,
                "allow_members_to_post_url": allow_members_to_post_url,
                "guidelines": guidelines,
            },
            return_type=CreateGroupResponse,
        )

    async def pin_group(self, group_id: int):
        return await self.__client.request(
            "POST", config.API_HOST + "/v1/pinned/groups", json={"id": group_id}
        )

    async def decline_moderator_offer(self, group_id: int):
        return await self.__client.request(
            "DELETE", config.API_HOST + f"/v1/groups/{group_id}/deputize"
        )

    async def decline_ownership_offer(self, group_id: int):
        return await self.__client.request(
            "DELETE", config.API_HOST + f"/v1/groups/{group_id}/transfer"
        )

    async def decline_group_join_request(self, group_id: int, user_id: int):
        return await self.__client.request(
            "POST", config.API_HOST + f"/v1/groups/{group_id}/decline/{user_id}"
        )

    async def unpin_group(self, group_id: int):
        return await self.__client.request(
            "DELETE", config.API_HOST + f"/v1/pinned/groups/{group_id}"
        )

    async def get_banned_group_members(
        self, group_id: int, page: int = None
    ) -> UsersResponse:
        params = {}
        if page:
            params["page"] = page
        return await self.__client.request(
            "GET", config.API_HOST + f"/v1/groups/{group_id}/ban_list", params=params
        )

    async def get_group_categories(self, **params) -> GroupCategoriesResponse:
        """

        Parameters:
        -----------

            - page: int - (optional)
            - number: int - (optional)

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v1/groups/categories",
            params=params,
            return_type=GroupCategoriesResponse,
        )

    async def get_create_group_quota(self) -> CreateGroupQuota:
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v1/groups/created_quota",
            return_type=CreateGroupQuota,
        )

    async def get_group(self, group_id: int) -> GroupResponse:
        return await self.__client.request(
            "GET",
            config.API_HOST + f"/v1/groups/{group_id}",
            return_type=GroupResponse,
        )

    async def get_groups(self, **params) -> GroupsResponse:
        """

        Parameters:
        -----------

            - group_category_id: int = None
            - keyword: str = None
            - from_timestamp: int = None
            - sub_category_id: int = None

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v2/groups",
            params=params,
            return_type=GroupsResponse,
        )

    async def get_invitable_users(
        self, group_id: int, **params
    ) -> UsersByTimestampResponse:
        """

        Parameters:
        -----------

            - from_timestamp: int - (optional)
            - user[nickname]: str - (optional)

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + f"/v1/groups/{group_id}/users/invitable",
            params=params,
            return_type=UsersByTimestampResponse,
        )

    async def get_joined_statuses(self, ids: list[int]) -> dict:
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v1/groups/joined_statuses",
            params={"ids": ids},
        )

    async def get_group_member(self, group_id: int, user_id: int) -> GroupUserResponse:
        return await self.__client.request(
            "GET", config.API_HOST + f"/v1/groups/{group_id}/members/{user_id}"
        )

    async def get_group_members(self, group_id: int, **params) -> GroupUsersResponse:
        """

        Parameters:
        -----------

            - id: int - (required)
            - mode: str - (optional)
            - keyword: str - (optional)
            - from_id: int - (optional)
            - from_timestamp: int - (optional)
            - order_by: str - (optional)
            - followed_by_me: bool - (optional)

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + f"/v2/groups/{group_id}/members",
            params=params,
            return_type=GroupUsersResponse,
        )

    async def get_my_groups(self, from_timestamp=None) -> GroupsResponse:
        params = {}
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v2/groups/mine",
            params=params,
            return_type=GroupsResponse,
        )

    async def get_relatable_groups(
        self, group_id: int, **params
    ) -> GroupsRelatedResponse:
        """

        Parameters:
        -----------

            - group_id: int - (required)
            - keyword: str - (optional)
            - from: str - (optional)

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + f"/v1/groups/{group_id}/relatable",
            params=params,
            return_type=GroupsRelatedResponse,
        )

    async def get_related_groups(
        self, group_id: int, **params
    ) -> GroupsRelatedResponse:
        """

        Parameters:
        -----------

            - group_id: int - (required)
            - keyword: str - (optional)
            - from: str - (optional)

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + f"/v1/groups/{group_id}/related",
            params=params,
            return_type=GroupsRelatedResponse,
        )

    async def get_user_groups(self, **params) -> GroupsResponse:
        """

        Parameters:
        -----------

            - user_id: int - (required)
            - page: int - (optional)

        """
        return await self.__client.request(
            "GET",
            config.API_HOST + "/v1/groups/user_group_list",
            params=params,
            return_type=GroupsResponse,
        )

    async def invite_users_to_group(
        self,
        group_id: int,
        user_ids: list[int],
    ):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/invite",
            json={"user_ids": user_ids},
        )

    async def join_group(
        self,
        group_id: int,
    ):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/join",
        )

    async def leave_group(
        self,
        group_id: int,
    ):
        return await self.__client.request(
            "DELETE",
            config.API_HOST + f"/v1/groups/{group_id}/leave",
        )

    async def remove_group_cover(
        self,
        group_id: int,
    ):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/remove_cover",
        )

    async def remove_moderator(
        self,
        group_id: int,
        user_id: int,
    ):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/fire/{user_id}",
        )

    async def remove_related_groups(
        self,
        group_id: int,
        related_group_ids: list[int],
    ):
        return await self.__client.request(
            "DELETE",
            config.API_HOST + f"/v1/groups/{group_id}/related",
            params={"related_group_id[]": related_group_ids},
        )

    async def send_moderator_offers(self, group_id: int, user_ids: list[int]):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v3/groups/{group_id}/deputize/mass",
            json={
                "user_ids": user_ids,
                "uuid": self.__client.device_uuid,
                "api_key": config.API_KEY,
                "timestamp": int(datetime.now().timestamp()),
                "signed_info": md5(
                    self.__client.device_uuid, int(datetime.now().timestamp()), True
                ),
            },
        )

    async def send_ownership_offer(self, group_id: int, user_id: int):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v3/groups/{group_id}/transfer",
            json={
                "user_id": user_id,
                "uuid": self.__client.device_uuid,
                "api_key": config.API_KEY,
                "timestamp": int(datetime.now().timestamp()),
                "signed_info": md5(
                    self.__client.device_uuid, int(datetime.now().timestamp()), True
                ),
            },
        )

    async def set_group_title(self, group_id: int, title: str):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/set_title",
            json={"title": title},
        )

    async def take_over_group_ownership(self, group_id: int):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/take_over",
        )

    async def unban_group_member(self, group_id: int, user_id: int):
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v1/groups/{group_id}/unban/{user_id}",
        )

    async def update_group(
        self,
        group_id: int,
        topic: str,
        description: str = None,
        secret: bool = None,
        hide_reported_posts: bool = None,
        hide_conference_call: bool = None,
        is_private: bool = None,
        only_verified_age: bool = None,
        only_mobile_verified: bool = None,
        call_timeline_display: bool = None,
        allow_ownership_transfer: bool = None,
        allow_thread_creation_by: str = None,
        gender: int = None,
        generation_groups_limit: int = None,
        group_category_id: int = None,
        cover_image_filename: str = None,
        sub_category_id: str = None,
        hide_from_game_eight: bool = None,
        allow_members_to_post_media: bool = None,
        allow_members_to_post_url: bool = None,
        guidelines: str = None,
    ) -> GroupResponse:
        return await self.__client.request(
            "POST",
            config.API_HOST + f"/v3/groups/{group_id}/update",
            json={
                "topic": topic,
                "description": description,
                "secret": secret,
                "hide_reported_posts": hide_reported_posts,
                "hide_conference_call": hide_conference_call,
                "is_private": is_private,
                "only_verified_age": only_verified_age,
                "only_mobile_verified": only_mobile_verified,
                "call_timeline_display": call_timeline_display,
                "allow_ownership_transfer": allow_ownership_transfer,
                "allow_thread_creation_by": allow_thread_creation_by,
                "gender": gender,
                "generation_groups_limit": generation_groups_limit,
                "group_category_id": group_category_id,
                "cover_image_filename": cover_image_filename,
                "sub_category_id": sub_category_id,
                "uuid": self.__client.device_uuid,
                "api_key": config.API_KEY,
                "timestamp": int(datetime.now().timestamp()),
                "signed_info": md5(
                    self.__client.device_uuid, int(datetime.now().timestamp()), True
                ),
                "hide_from_game_eight": hide_from_game_eight,
                "allow_members_to_post_image_and_video": allow_members_to_post_media,
                "allow_members_to_post_url": allow_members_to_post_url,
                "guidelines": guidelines,
            },
            return_type=GroupResponse,
        )

    async def withdraw_moderator_offer(self, group_id: int, user_id: int):
        return await self.__client.request(
            "PUT",
            config.API_HOST + f"/v1/groups/{group_id}/deputize/{user_id}/withdraw",
        )

    async def withdraw_ownership_offer(self, group_id: int, user_id: int):
        return await self.__client.request(
            "PUT",
            config.API_HOST + f"/v1/groups/{group_id}/transfer/withdraw",
            json={"user_id": user_id},
        )
