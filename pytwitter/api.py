"""
    Api Impl
"""
from typing import List, Optional, Tuple, Union

import requests
from requests.models import Response
from requests_oauthlib import OAuth2

import pytwitter.models as md
from pytwitter.error import PyTwitterError
from pytwitter.utils.validators import enf_comma_separated


class Api:
    BASE_URL_V2 = "https://api.twitter.com/2"

    def __init__(
        self,
        bearer_token=None,
        consumer_key=None,
        consumer_secret=None,
        access_token=None,
        access_secret=None,
        application_only_auth=False,
        oauth_flow=False,  # provide access with authorize
        timeout=None,
        proxies=None,
    ):
        self.session = requests.Session()
        self._auth = None
        self.timeout = timeout
        self.proxies = proxies

        # just use bearer token
        if bearer_token:
            self._auth = OAuth2(
                token={"access_token": bearer_token, "token_type": "Bearer"}
            )
        # use app auth
        elif consumer_key and consumer_secret and application_only_auth:
            pass
        # use user auth
        elif all([consumer_key, consumer_secret, access_token, access_secret]):
            pass
        # use oauth flow by hand
        elif consumer_key and consumer_secret and oauth_flow:
            pass
        else:
            raise Exception("Need oauth")

    def set_credentials(self):
        pass

    def _request(self, url, verb="GET", params=None, data=None, enforce_auth=True):
        """
        Request for twitter api url
        :param url: The api location for twitter
        :param verb: HTTP Method, either GET or POST
        :param params: The url params for GET
        :param data: The query data for POST
        :param enforce_auth: Whether need auth
        :return: A json object
        """
        auth = None
        if enforce_auth:
            if not self._auth:
                raise Exception("The twitter.Api instance must be authenticated.")

            auth = self._auth

        resp = self.session.request(
            url=url,
            method=verb,
            params=params,
            data=data,
            auth=auth,
            timeout=self.timeout,
            proxies=self.proxies,
        )
        return resp

    @staticmethod
    def _parse_response(resp: Response) -> dict:
        """
        :param resp: Response
        :return: json data
        """
        try:
            data = resp.json()
        except ValueError:
            raise PyTwitterError(f"Unknown error: {resp.content}")

        if "errors" in data:
            raise PyTwitterError(data["errors"])

        return data

    def users_by_ids(
        self,
        *,
        ids: Union[str, List, Tuple],
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns a variety of information about one or more users specified by the requested IDs.

        :param ids: The IDs for target users, Up to 100 are allowed in a single request.
        :param user_fields: Fields for the user object.
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for expansions.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the users
            - includes: expansions data.
        """

        args = {
            "ids": enf_comma_separated(name="ids", value=ids),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
        }

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users",
            params=args,
        )
        data = self._parse_response(resp)

        data, includes = data["data"], data.get("includes")
        if return_json:
            return data, includes
        else:
            return (
                [md.User.new_from_json_dict(d) for d in data],
                md.Includes.new_from_json_dict(includes),
            )

    def user_by_id(
        self,
        *,
        user_id: str,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns a variety of information about a single user specified by the requested ID.

        :param user_id: The ID of the user
        :param user_fields: Fields for the user object.
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for expansions.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the user
            - includes: expansions data.
        """

        args = {
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
        }

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}",
            params=args,
        )
        data = self._parse_response(resp)

        data, includes = data["data"], data.get("includes")
        if return_json:
            return data, includes
        else:
            return (
                md.User.new_from_json_dict(data),
                md.Includes.new_from_json_dict(includes),
            )