from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings


_client = Client(
    transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)


def query_info_object_by_link(link):
    return _client.execute(
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


def update_info_object(info_object, ddcs, keywords_to_remove):
        _client.execute(
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
                  "input": {
                    "filter": { "link": { "eq": info_object["link"] } },
                    "set": { "class": ddcs },
                    "remove": { "keywords": keywords_to_remove }
                  }
            }
        )
