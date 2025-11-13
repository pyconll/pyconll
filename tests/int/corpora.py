"""
Registration of all corpora for testing. This works as a sort of cache key or requirements file for
action workflows.
"""

from dataclasses import dataclass


@dataclass
class CorporaRegistration:
    """
    Info to register an online resource as a corpora that can be tested against.
    """

    version: str
    url: str
    zip_hash: str
    contents_hash: str


# This is the registration for the different corpora. It includes an id, and a
# method of creation as a key-value pair. This registration structure allows
# for the same corpora to easily be used in different tests which are designed
# to holistically evaluate pyconll across large scenarios, like correctness or
# performance. Given the structure of exceptions and marks, I may still need
# some tweaking of what structure works best, but this is a definite improvement
# and is on a path toward more flexibility and robustness.
corpora = [
    CorporaRegistration(
        "2.16",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5901/ud-treebanks-v2.16.tgz",
        "87710204b6441736a8a9fed779585aa88b6eeafe231fa2ed9282c0cd9e30960b",
        "6b38dc116ec0da5177b8808e5bead78a4d85cdd47ce007eede99df25b48b27e9",
    ),
    CorporaRegistration(
        "2.15",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5787/ud-treebanks-v2.15.tgz",
        "24ddd9a7e6a291f3882c13febb4d97accfbc6f51633a867963c19e6004d7df97",
        "f84959120d53a701325ba15b3abcb819be8ceda3d1ec6d5edbeda7b5f8b3a358",
    ),
    CorporaRegistration(
        "2.14",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5502/ud-treebanks-v2.14.tgz",
        "a710e09f977fc1ca4aeaf200806a75fbbc46d2c0717c70933a94ad78129ee1af",
        "f6dc84752cce6087b26fd97522dd7171df82492c1004d80e2f6f0224a750c7e5",
    ),
    CorporaRegistration(
        "2.13",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5287/ud-treebanks-v2.13.tgz",
        "d6538ed4c05508be3bb7d9c3448de1062f6f9958c833b93558df300e4b1d3781",
        "57c44ceda3d7b89bc9f84238b73363d09a1d895f34b29e1dad4a5e6e3d1f0cea",
    ),
    CorporaRegistration(
        "2.12",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5150/ud-treebanks-v2.12.tgz",
        "24f876d5ad9dbdc639a33a73f02d12ddfe582e8d4e7f5d08978c8a86680d088c",
        "68152f141a2653a183865cef4ddc64ae146c76fd6effd724c99c2145c80f213c",
    ),
    CorporaRegistration(
        "2.11",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4923/ud-treebanks-v2.11.tgz",
        "d75f7df726761836f797fe6c001c7a1ecce93d93129414ef57cf2262d15707e8",
        "59a87cfbb82524d6dbf4aa27c0c8a8d35fd3e5d3cca3493875a6c4b2c5031a40",
    ),
    CorporaRegistration(
        "2.10",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4758/ud-treebanks-v2.10.tgz",
        "f6deca6ab803abdfa8dca911600f6bc5f214267e348acbd59fd4c4b88db14ea6",
        "572d09f96d52a949750e99caa36519daa3fac366a7643d97e37498873c2ad104",
    ),
    CorporaRegistration(
        "2.9",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4611/ud-treebanks-v2.9.tgz",
        "ca0162be47151a55a5c6c5de24db821c76d67f322fcdfa3fe1436891e9bf2232",
        "7fed278e47358be198303e51f1afca9d77985db550d69c685bbcd5d066d78915",
    ),
    CorporaRegistration(
        "2.8",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3687/ud-treebanks-v2.8.tgz",
        "95d2f4370dc5fe93653eb36e7268f4ec0c1bd012e51e943d55430f1e9d0d7e05",
        "eb5d8941be917d2cb46677cb575f18dd6218bddec446b428a5b96d96ab44c0cd",
    ),
    CorporaRegistration(
        "2.7",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3424/ud-treebanks-v2.7.tgz",
        "ee61f186ac5701440f9d2889ca26da35f18d433255b5a188b0df30bc1525502b",
        "38e7d484b0125aaf7101a8c447fd2cb3833235cf428cf3c5749128ade73ecee2",
    ),
    CorporaRegistration(
        "2.6",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v2.6.tgz",
        "a462a91606c6b2534a767bbe8e3f154b678ef3cc81b64eedfc9efe9d60ceeb9e",
        "a28fdc1bdab09ad597a873da62d99b268bdfef57b64faa25b905136194915ddd",
    ),
    CorporaRegistration(
        "2.5",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz",
        "5ff973e44345a5f69b94cc1427158e14e851c967d58773cc2ac5a1d3adaca409",
        "4761846e8c5f7ec7e40a6591f7ef5307ca9e7264da894d05d135514a4ea22a10",
    ),
    CorporaRegistration(
        "2.4",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz",
        "252a937038d88587842f652669cdf922b07d0f1ed98b926f738def662791eb62",
        "000646eb71cec8608bd95730d41e45fac319480c6a78132503e0efe2f0ddd9a9",
    ),
    CorporaRegistration(
        "2.3",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz",
        "122e93ad09684b971fd32b4eb4deeebd9740cd96df5542abc79925d74976efff",
        "359e1989771268ab475c429a1b9e8c2f6c76649b18dd1ff6568c127fb326dd8f",
    ),
    CorporaRegistration(
        "2.2",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz",
        "a9580ac2d3a6d70d6a9589d3aeb948fbfba76dca813ef7ca7668eb7be2eb4322",
        "fa3a09f2c4607e19d7385a5e975316590f902fa0c1f4440c843738fbc95e3e2a",
    ),
    CorporaRegistration(
        "2.1",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2515/ud-treebanks-v2.1.tgz",
        "446cc70f2194d0141fb079fb22c05b310cae9213920e3036b763899f349fee9b",
        "36921a1d8410dc5e22ef9f64d95885dc60c11811a91e173e1fd21706b83fdfee",
    ),
    CorporaRegistration(
        "2.0",
        "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1983/ud-treebanks-v2.0.tgz",
        "c6c6428f709102e64f608e9f251be59d35e4add1dd842d8dc5a417d01415eb29",
        "4f08c84bec5bafc87686409800a9fe9b5ac21434f0afd9afe1cc12afe8aa90ab",
    ),
]
