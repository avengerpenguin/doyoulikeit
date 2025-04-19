import bz2
import json
import sys

from tqdm import tqdm
import pydash


REQUIRED = [
    "labels.en.value",
    "claims.P18[0].mainsnak.datavalue.value",
    "sitelinks.enwiki.site",
]


with bz2.open(sys.argv[1], mode="rt") as file_obj:
    with tqdm(total=1745942101095) as pbar:
        file_obj.read(2)  # We expect the file to start with "{\n"
        pbar.update(2)
        for line in file_obj:
            if line.startswith("]"):
                break
            data = json.loads(line.rstrip(",\n"))

            for required in REQUIRED:
                if not pydash.get(data, required):
                    break
            else:
                print(f"""{len(data["claims"])}\t{data["id"]}""")

            pbar.update(len(line))
