from bw_processing import load_datapackage, create_datapackage
from bw_processing.constants import INDICES_DTYPE
from bw_processing.errors import PotentialInconsistency
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import shutil
from fs.osfs import OSFS
from fs.memoryfs import MemoryFS


class Dummy:
    pass


def add_data(dp):
    data_array = np.array([(2, 7, 12)])
    indices_array = np.array([(1, 4), (2, 5), (3, 6)], dtype=INDICES_DTYPE)
    flip_array = np.array([1, 0, 0], dtype=bool)
    dp.add_persistent_vector(
        matrix="sa_matrix",
        data_array=data_array,
        name="sa-data-vector",
        indices_array=indices_array,
        nrows=2,
        flip_array=flip_array,
    )

    json_data = [{"a": "b"}, 1, True]
    json_parameters = ["a", "foo"]
    df = pd.DataFrame(
        [
            {"id": 1, "a": 1, "c": 3, "d": 11},
            {"id": 2, "a": 2, "c": 4, "d": 11},
            {"id": 3, "a": 1, "c": 4, "d": 11},
        ]
    ).set_index(["id"])

    dp.add_persistent_array(
        matrix="sa_matrix",
        data_array=np.arange(12).reshape((3, 4)),
        indices_array=indices_array,
        name="sa-data-array",
        flip_array=flip_array,
    )

    dp.add_dynamic_vector(
        interface=Dummy(),
        indices_array=indices_array,
        matrix="sa_matrix",
        name="sa-vector-interface",
    )

    dp.add_dynamic_array(
        interface=Dummy(),
        matrix="sa_matrix",
        name="sa-array-interface",
        indices_array=indices_array,
    )
    dp.add_csv_metadata(
        dataframe=df,
        valid_for=[("sa-data-vector", "rows")],
        name="sa-data-vector-csv-metadata",
    )
    dp.add_json_metadata(
        data=json_data, valid_for="sa-data-array", name="sa-data-array-json-metadata"
    )


def copy_fixture(fixture_name, dest):
    source = Path(__file__).parent.resolve() / "fixtures" / fixture_name
    for fp in source.iterdir():
        shutil.copy(fp, dest / fp.name)


def test_del_resource_filesystem(tmp_path):
    copy_fixture("tfd", tmp_path)
    dp = load_datapackage(OSFS(str(tmp_path)))
    reference_length = len(dp)
    assert "sa-vector-interface.indices.npy" in [o.name for o in tmp_path.iterdir()]
    dp.del_resource("sa-vector-interface.indices")
    assert "sa-vector-interface.indices.npy" not in [o.name for o in tmp_path.iterdir()]
    assert len(dp) == reference_length - 1
    assert len(dp.data) == reference_length - 1
    assert len(dp.metadata["resources"]) == reference_length - 1
    assert len(dp.resources) == reference_length - 1


def test_del_resource_in_memory():
    dp = create_datapackage()
    add_data(dp)
    assert isinstance(dp.fs, MemoryFS)

    reference_length = len(dp)
    print(dp.resources)
    assert "sa-vector-interface.indices" in [o["name"] for o in dp.resources]
    dp.del_resource("sa-vector-interface.indices")
    assert "sa-vector-interface.indices" not in [o["name"] for o in dp.resources]
    assert len(dp) == reference_length - 1
    assert len(dp.data) == reference_length - 1
    assert len(dp.metadata["resources"]) == reference_length - 1
    assert len(dp.resources) == reference_length - 1


def test_del_resource_error_modifications(tmp_path):
    copy_fixture("tfd", tmp_path)
    dp = load_datapackage(OSFS(str(tmp_path)))
    dp._modified = [1]
    with pytest.raises(PotentialInconsistency):
        dp.del_resource(1)
