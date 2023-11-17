import logging
import re

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from settings import settings

logger = logging.getLogger(__name__)

logger.info(f"use {settings.DB_HOST} as gql endpoint")

graphql_client = None # Client(transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"))

def query_info_object_by_link(link):
    return graphql_client.execute(
        gql(
            """
            query getInfoObject($link: String!) {
                getInfoObject(link: $link) {
                    link
                    keywords {
                        name
                    }
                    class {
                        id
                        name
                    }
                }
            }
            """
        ),
        variable_values={ "link": link }
    )["getInfoObject"]


def update_info_object(input):
        graphql_client.execute(
            gql(
                """
                mutation updateInfoObject($input: UpdateInfoObjectInput!) {
                    updateInfoObject(input: $input) {
                        infoObject {
                            link
                        }
                    }
                }
                """
            ),
            variable_values={
                  "input": input
            }
        )


def run(link):
    logging.info(f"Resolving classifications for link {link}")

    global graphql_client

    if graphql_client is None:
        logger.info(f"connect to database at '{settings.DB_HOST}'")
        graphql_client = Client(transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"))

    info_object = query_info_object_by_link(link)

    if not info_object:
        return
    
    keywords_to_remove = []
    classifications = []

    for keyword in info_object["keywords"]:
        is_classification = bool(re.match(r"(?:\d{3}\.\d+|\d{3}):", keyword["name"]))
        if is_classification:
            keywords_to_remove.append(keyword)
            values = keyword["name"].split(":")
            classifications.append({ "id": values[0].strip(), "name": values[1].strip() })

    info_object_classifications = { classification["id"] for classification in info_object["class"] }

    new_classifications = [
        classification
        for classification in classifications 
        if classification["id"] not in info_object_classifications
    ]

    logger.info(f"Found {len(new_classifications)} classifications in keywords field")
    
    if not (len(keywords_to_remove) + len(classifications)):
        return

    update_info_object(
        {
            "filter": { "link": { "eq": info_object["link"] } },
            "set": { "class": new_classifications },
            "remove": { "keywords": keywords_to_remove }
        }
    )
