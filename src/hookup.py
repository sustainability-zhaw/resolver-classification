import re
import db


def run(routing_key, body):
    info_object = db.query_info_object_by_link(body['link'])

    if not info_object:
        return
    
    keywords_to_remove = []
    ddcs = []

    for keyword in info_object["keywords"]:
        is_ddc = bool(re.match(r"(?:\d{3}\.\d+|\d{3}):", keyword["name"]))
        if is_ddc:
            keywords_to_remove.append(keyword)
            values = keyword["name"].split(":")
            ddcs.append({ "id": values[0].strip(), "name": values[1].strip() })
    
    if not len(ddcs):
        return

    db.update_info_object(
        {
            "filter": { "link": { "eq": info_object["link"] } },
            "set": { "class": ddcs },
            "remove": { "keywords": keywords_to_remove }
        }
    )
