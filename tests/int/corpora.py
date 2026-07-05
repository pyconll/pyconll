"""
Registration of all corpora for testing. This works as a sort of cache key or requirements file for
action workflows.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import boto3


class CorpusSource(Protocol):
    def filename(self) -> str:
        """Return the local filename to use when storing this corpus artifact."""
        ...

    def download_to(self, dest: Path, chunk_size: int) -> None:
        """
        Download the corpus artifact to the given destination path.

        Args:
            dest: The full path (including filename) to write the downloaded artifact to.
            chunk_size: The number of bytes to read per chunk when streaming the download.
        """
        ...


@dataclass
class AwsS3Object:
    bucket: str
    key: str
    region: str

    def filename(self) -> str:
        return Path(self.key).name

    def download_to(self, dest: Path, chunk_size: int) -> None:
        s3 = boto3.Session().client("s3", region_name=self.region)
        response = s3.get_object(Bucket=self.bucket, Key=self.key)

        with open(str(dest), "wb") as f:
            for chunk in response["Body"].iter_chunks(chunk_size=chunk_size):
                f.write(chunk)


@dataclass
class CorporaRegistration:
    """
    Info to register an online resource as a corpora that can be tested against.
    """

    version: str
    url: CorpusSource
    zip_hash: str
    contents_hash: str


_BUCKET = "pyconll-881490118399-us-east-1-an"
_REGION = "us-east-1"

# This is the registration for the different corpora. It includes an id, and a
# method of creation as a key-value pair. This registration structure allows
# for the same corpora to easily be used in different tests which are designed
# to holistically evaluate pyconll across large scenarios, like correctness or
# performance. Given the structure of exceptions and marks, I may still need
# some tweaking of what structure works best, but this is a definite improvement
# and is on a path toward more flexibility and robustness.
corpora = [
    CorporaRegistration(
        "2.18",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.18.tgz", region=_REGION),
        "a93fe8520bc4c5ff34670d9a93a5a7689c018c1e59643fa27e03036717841b8a",
        "75293bd718b3271512740cb463267c87fbb5062506938efec905cc900cd84e69",
    ),
    CorporaRegistration(
        "2.17",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.17.tgz", region=_REGION),
        "bf30726e238f9c4379ffb0d6f8c3eaf4ecad9f72ab42104b0130b61603915872",
        "13b70a1394dbf5dd8310bea05dd83b5f4a2969939862bc2d93d4da4ad877c1f0",
    ),
    CorporaRegistration(
        "2.16",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.16.tgz", region=_REGION),
        "87710204b6441736a8a9fed779585aa88b6eeafe231fa2ed9282c0cd9e30960b",
        "6b38dc116ec0da5177b8808e5bead78a4d85cdd47ce007eede99df25b48b27e9",
    ),
    CorporaRegistration(
        "2.15",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.15.tgz", region=_REGION),
        "24ddd9a7e6a291f3882c13febb4d97accfbc6f51633a867963c19e6004d7df97",
        "f84959120d53a701325ba15b3abcb819be8ceda3d1ec6d5edbeda7b5f8b3a358",
    ),
    CorporaRegistration(
        "2.14",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.14.tgz", region=_REGION),
        "a710e09f977fc1ca4aeaf200806a75fbbc46d2c0717c70933a94ad78129ee1af",
        "f6deca6ab803abdfa8dca911600f6bc5f214267e348acbd59fd4c4b88db14ea6",
    ),
    CorporaRegistration(
        "2.13",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.13.tgz", region=_REGION),
        "d6538ed4c05508be3bb7d9c3448de1062f6f9958c833b93558df300e4b1d3781",
        "57c44ceda3d7b89bc9f84238b73363d09a1d895f34b29e1dad4a5e6e3d1f0cea",
    ),
    CorporaRegistration(
        "2.12",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.12.tgz", region=_REGION),
        "24f876d5ad9dbdc639a33a73f02d12ddfe582e8d4e7f5d08978c8a86680d088c",
        "68152f141a2653a183865cef4ddc64ae146c76fd6effd724c99c2145c80f213c",
    ),
    CorporaRegistration(
        "2.11",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.11.tgz", region=_REGION),
        "d75f7df726761836f797fe6c001c7a1ecce93d93129414ef57cf2262d15707e8",
        "59a87cfbb82524d6dbf4aa27c0c8a8d35fd3e5d3cca3493875a6c4b2c5031a40",
    ),
    CorporaRegistration(
        "2.10",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.10.tgz", region=_REGION),
        "f6deca6ab803abdfa8dca911600f6bc5f214267e348acbd59fd4c4b88db14ea6",
        "572d09f96d52a949750e99caa36519daa3fac366a7643d97e37498873c2ad104",
    ),
    CorporaRegistration(
        "2.9",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.9.tgz", region=_REGION),
        "ca0162be47151a55a5c6c5de24db821c76d67f322fcdfa3fe1436891e9bf2232",
        "7fed278e47358be198303e51f1afca9d77985db550d69c685bbcd5d066d78915",
    ),
    CorporaRegistration(
        "2.8",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.8.tgz", region=_REGION),
        "95d2f4370dc5fe93653eb36e7268f4ec0c1bd012e51e943d55430f1e9d0d7e05",
        "eb5d8941be917d2cb46677cb575f18dd6218bddec446b428a5b96d96ab44c0cd",
    ),
    CorporaRegistration(
        "2.7",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.7.tgz", region=_REGION),
        "ee61f186ac5701440f9d2889ca26da35f18d433255b5a188b0df30bc1525502b",
        "38e7d484b0125aaf7101a8c447fd2cb3833235cf428cf3c5749128ade73ecee2",
    ),
    CorporaRegistration(
        "2.6",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.6.tgz", region=_REGION),
        "a462a91606c6b2534a767bbe8e3f154b678ef3cc81b64eedfc9efe9d60ceeb9e",
        "a28fdc1bdab09ad597a873da62d99b268bdfef57b64faa25b905136194915ddd",
    ),
    CorporaRegistration(
        "2.5",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.5.tgz", region=_REGION),
        "5ff973e44345a5f69b94cc1427158e14e851c967d58773cc2ac5a1d3adaca409",
        "4761846e8c5f7ec7e40a6591f7ef5307ca9e7264da894d05d135514a4ea22a10",
    ),
    CorporaRegistration(
        "2.4",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.4.tgz", region=_REGION),
        "252a937038d88587842f652669cdf922b07d0f1ed98b926f738def662791eb62",
        "000646eb71cec8608bd95730d41e45fac319480c6a78132503e0efe2f0ddd9a9",
    ),
    CorporaRegistration(
        "2.3",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.3.tgz", region=_REGION),
        "122e93ad09684b971fd32b4eb4deeebd9740cd96df5542abc79925d74976efff",
        "359e1989771268ab475c429a1b9e8c2f6c76649b18dd1ff6568c127fb326dd8f",
    ),
    CorporaRegistration(
        "2.2",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.2.tgz", region=_REGION),
        "a9580ac2d3a6d70d6a9589d3aeb948fbfba76dca813ef7ca7668eb7be2eb4322",
        "fa3a09f2c4607e19d7385a5e975316590f902fa0c1f4440c843738fbc95e3e2a",
    ),
    CorporaRegistration(
        "2.1",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.1.tgz", region=_REGION),
        "446cc70f2194d0141fb079fb22c05b310cae9213920e3036b763899f349fee9b",
        "36921a1d8410dc5e22ef9f64d95885dc60c11811a91e173e1fd21706b83fdfee",
    ),
    CorporaRegistration(
        "2.0",
        AwsS3Object(bucket=_BUCKET, key="ud-treebanks-v2.0.tgz", region=_REGION),
        "c6c6428f709102e64f608e9f251be59d35e4add1dd842d8dc5a417d01415eb29",
        "4f08c84bec5bafc87686409800a9fe9b5ac21434f0afd9afe1cc12afe8aa90ab",
    ),
]
