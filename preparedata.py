import csv
import json
import re

bank_registry_f = open("sepa-zv-vz_gesamt.csv", "r", encoding="latin_1")
for i in range(5):
    bank_registry_f.readline()

bank_registry_read = csv.DictReader(bank_registry_f, delimiter=";")
bank_registry = list(bank_registry_read)
bank_registry_f.close()

sepa_instant_f = open("sepa_instant_credit_transfer.csv", "r", encoding="utf-8")
sepa_instant_read = csv.DictReader(sepa_instant_f, delimiter=",")
sepa_instant = {sepa_bank["BIC"]: sepa_bank for sepa_bank in sepa_instant_read}
sepa_instant_f.close()

sepa_transfer_f = open("sepa_credit_transfer.csv", "r", encoding="utf-8")
sepa_transfer_read = csv.DictReader(sepa_transfer_f, delimiter=",")
sepa_transfer = list(sepa_transfer_read)
sepa_transfer_f.close()

def smartcaps(s):
    """Fixes capitalization for all caps word with a length greater than 3"""
    words = re.split(r"([^a-zA-Z]+)", s)
    newwords = []
    for word in words:
        if (len(word) <= 3) or (not word.isupper()):
            newwords.append(word)
        else:
            newwords.append(word.capitalize())
    return "".join(newwords)

def normalize_bic(bic):
    if bic.endswith("XXX"):
        return bic[:-3].upper()
    else:
        return bic.upper()

def normalize_blz(blz):
    if len(blz) < 5:
        return "00000"[len(blz):] + blz
    else:
        return blz

blz_map = {
    normalize_blz(oe_bank["Bankleitzahl"]): normalize_bic(oe_bank["SWIFT-Code"])
    for oe_bank in bank_registry
}

sepa_info = {
    normalize_bic(sepa_bank["BIC"]): {
        "country": smartcaps(sepa_bank["Country"]),
        "name": smartcaps(sepa_bank["ParticipantName"]),
        "address": smartcaps(sepa_bank["Address"]),
        "city": smartcaps(sepa_bank["City"]),
        "sepa_readiness": sepa_bank["Readiness Date"],
        "instant_readiness":
            sepa_instant.get(sepa_bank["BIC"], {}).get("Readiness Date")
    }
    for sepa_bank in sepa_transfer
}

with open("bankinfo.js", "w") as merged_f:
    merged_f.write("BLZ_MAP = ");
    json.dump(blz_map, merged_f, indent=2)
    merged_f.write("\n\nSEPA_INFO = ");
    json.dump(sepa_info, merged_f, indent=2)
