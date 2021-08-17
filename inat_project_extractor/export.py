import logging
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def _get_latitude(geojson: dict) -> Optional[float]:
    if geojson.get("type", "?") != "Point":
        return None

    return geojson["coordinates"][1];


def _get_longitude(geojson: dict) -> Optional[float]:
    if geojson.get("type", "?") != "Point":
        return None

    return geojson["coordinates"][0];


def _get_photo_url(taxon: dict) -> Optional[str]:
    if "default_photo" in taxon:
        return taxon["default_photo"]["medium_url"]

    return None


def _get_sound_url(sounds: list) -> Optional[str]:
    if len(sounds) > 0:
        return sounds[0]["file_url"]

    return None


def _get_tag_list(tags: list) -> Optional[str]:
    if len(tags) > 0:
        return ", ".join(tags)

    return None


def _flatten_data(results: List[dict]) -> List[dict]:
    observations = list()

    for r in results:
        try:
            logger.debug(f"Flattening observation {r['id']}")

            o = {
                "scientific_name": r["taxon"]["name"],
                "taxon_id": r["taxon"]["id"],
                "time_zone": r["created_time_zone"],
                "latitude": _get_latitude(r["geojson"]),
                "longitude": _get_longitude(r["geojson"]),
                "coordinates_obscured": r["obscured"],
                "user_id": r["user"]["id"],
                "user_login": r["user"]["login"],
                "license": r["license_code"],
                "url": f"http://www.inaturalist.org/observations/{r['id']}",
                "image_url": _get_photo_url(r["taxon"]),
                "sound_url": _get_sound_url(r["sounds"]),
                "tag_list": _get_tag_list(r["tags"]),
                "captive_cultivated": r["captive"],
                "curator_coordinate_access": r["project_observations"][0][
                    "preferences"
                ]["allows_curator_coordinate_access"],
            }

            if "preferred_common_name" in r["taxon"]:
                # If the record does not have a species-level identification
                # then this field will be absent
                o["common_name"] = r["taxon"]["preferred_common_name"]

            direct_map = [
                "id",
                "species_guess",
                "iconic_taxon_name",
                "num_identification_agreements",
                "num_identification_disagreements",
                "observed_on_string",
                "observed_on",
                "time_observed_at",
                "place_guess",
                "positional_accuracy",
                "id_please",
                "private_place_guess",
                "private_latitude",
                "private_longitude",
                "private_positional_accuracy",
                "geoprivacy",
                "taxon_geoprivacy",
                "positioning_method",
                "positioning_device",
                "out_of_range",
                "tracking_code",
                "created_at",
                "updated_at",
                "quality_grade",
                "description",
                "oauth_application_id",
            ]

            for field in direct_map:
                if field in r:
                    o[field] = r[field]
                else:
                    o[field] = None

            ids = r["identifications"]
            for id in ids:
                if "curator" in id["user"]["roles"]:
                    o["curator_ident_taxon_id"] = id["taxon"]["id"]
                    o["curator_ident_taxon_name"] = id["taxon"]["name"]
                    o["curator_ident_user_id"] = id["user"]["id"]
                    o["curator_ident_user_login"] = id["user"]["login"]
                    break

            for field in r["ofvs"]:
                o[f"field:{field['name'].lower()}"] = field["value"]

            observations.append(o)
        except BaseException as ex:
            logger.exception(ex)

    return observations


def export(file_path: str, results: List[dict]):
    """
    Writes data out to a CSV file in append mode.

    Parameters
    ----------
    file_path: str
        Full path to the output file.
    results: List[dict]
        A list of observations,  each of which is a dictionary
    """

    df = pd.DataFrame(_flatten_data(results))

    column_order = [
        "id",
        "species_guess",
        "scientific_name",
        "common_name",
        "iconic_taxon_name",
        "taxon_id",
        "id_please",
        "num_identification_agreements",
        "num_identification_disagreements",
        "observed_on_string",
        "observed_on",
        "time_observed_at",
        "time_zone",
        "place_guess",
        "latitude",
        "longitude",
        "positional_accuracy",
        "private_place_guess",
        "private_latitude",
        "private_longitude",
        "private_positional_accuracy",
        "geoprivacy",
        "taxon_geoprivacy",
        "coordinates_obscured",
        "positioning_method",
        "positioning_device",
        "out_of_range",
        "user_id",
        "user_login",
        "created_at",
        "updated_at",
        "quality_grade",
        "license",
        "url",
        "image_url",
        "sound_url",
        "tag_list",
        "description",
        "oauth_application_id",
        "captive_cultivated",
        "curator_ident_taxon_id",
        "curator_ident_taxon_name",
        "curator_ident_user_id",
        "curator_ident_user_login",
        "tracking_code",
        "curator_coordinate_access",
        "field:count",
        "field:distance to animal",
        "field:whooping crane habitat",
        "field:list of hazards present",
        "field:crane behavior",
        "field:well-being",
    ]

    df = df.reindex(columns=column_order)

    df.to_csv(file_path, index=False, mode="a")
