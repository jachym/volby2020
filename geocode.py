#!/usr/bin/env python3

import csv
import os
import requests
import json

kraje = []

cities = {}


def _get_kraj(nr):
    for item in os.listdir("data"):
        if item.find("-"):
            fnr,name = item.split("-")
            fnr = int(fnr)

            if nr == fnr:
                return os.path.join("data", item)

def geocode_partaj(fname, kname):

    candidates = []
    print(fname)
    with open(fname) as partaj_file:
        reader = csv.reader(partaj_file, delimiter=";")
        for row in reader:
            nr, name, vek, party, aff, work, city, votes, votesp = row

            if city not in cities:
                resp = requests.get("https://nominatim.openstreetmap.org/search?q={city},{kname}&format=geojson".format(city=city, kname=kname))
                data = resp.json()
                cities[city] = data["features"][0]

            candidate = {
                    "type":"Feature",
                    "properties":{
                        "nr":nr,
                        "name": name,
                        "vek": vek,
                        "party": party,
                        "aff": aff,
                        "work": work,
                        "city": city
                    },
                    "geometry": cities[city]["geometry"]
            }

            candidates.append(candidate)
    return candidates


def geocode_kraj(kdir, kname):

    candidates = []
    for strana in os.listdir(kdir):
        strana_file_name = os.path.join(kdir, strana)
        if os.path.isfile(strana_file_name):
            snr,sname = strana.split("-")

            candidates += geocode_partaj(strana_file_name, kname)

    candidates = {
            "type": "FeatureCollection",
            "features": candidates
    }

    with open(
            os.path.join("data", "mapy", os.path.basename(kdir)+".geojson"),
            "w") as mapa_out:
        
        json.dump(candidates, mapa_out, indent=4)




def main():

    with open("data/ciselniky/kraje.csv") as kraje_file:
        reader = csv.reader(kraje_file, delimiter=";")
        for i in reader:
            kraje.append(i)


    for kraj in kraje:
        nr, name = kraj
        nr = int(nr)

        kdir = _get_kraj(nr)

        geocode_kraj(kdir, name)




if __name__ == "__main__":
    main()

