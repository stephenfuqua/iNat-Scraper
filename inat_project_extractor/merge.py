import logging

import pandas as pd

from configuration import Configuration

logger = logging.getLogger(__name__)


def merge_bulk_and_api_files(config: Configuration, api_file: str) -> None:

    api_columns = [
        "id",
        "curator_coordinate_access",
        "curator_ident_taxon_id",
        "curator_ident_taxon_name",
        "curator_ident_user_id",
        "curator_ident_user_login",
        "id_please",
        "out_of_range",
        "tracking_code",
    ]

    dtypes = dict(zip(api_columns, ["int64", "str", "str", "str", "str", "str", "str", "str", "str"]))

    api_data = pd.read_csv(api_file, dtype=dtypes, quotechar='"')
    bulk_data = pd.read_csv(config.input_file, dtype=object, quotechar='"')

    bulk_data = bulk_data.astype({"id": "int64"})

    merge = bulk_data.merge(api_data[api_columns], on="id", how="left")

    merge_path = config.get_merge_file_output_path()

    logger.info(f"Writing merged file: {merge_path}")
    merge.to_csv(merge_path, index=False)
