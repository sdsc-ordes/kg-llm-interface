from aikg.config.chroma import Config, Location
from aikg.pipeline.chroma_build import chroma_build_flow


def test_build_chroma(schema_file, small_instance_file):
    loc = Location(instances_path=small_instance_file, schema_path=schema_file)
    chroma_build_flow(loc, Config())
