#!/usr/bin/env python3

import csv
import os
import requests
import json
from html.parser import HTMLParser
import lxml.html
import time

kraje = []

cities = {}

def _parse_kraj(nr):

    candidates = []

    with open("data/ciselniky/strany.csv") as strany_file:
        reader = csv.reader(strany_file, delimiter=";")

        for row in reader:
            strana_nr, zkratka, nazev,empty = row
            #print("    - {} {}".format(strana_nr, nazev))

            url = "https://volby.cz/pls/kz2020/kz111?xjazyk=CZ&xkraj={nr}&xstrana={strana}&xv=1&xt=2".format(nr=nr, strana=strana_nr)

            while True:
                try:
                    r = requests.get(url)
                    break
                except:
                    print("error, sleeping and trying again")
                    time.sleep(10)
            if r.status_code == 200:
                page = lxml.html.fromstring(r.text)
                trs = page.xpath('//table/tr')

                for tr in trs:
                    tds = tr.xpath("./td")
                    if len(tds) == 9:
                        #print([t.text for t in tds])
                        candidates.append([
                            int(tds[0].text),
                            tds[1].text,
                            int(tds[2].text),
                            tds[3].text,
                            tds[4].text,
                            tds[5].text,
                            tds[6].text,
                            int(tds[7].text),
                            float(tds[8].text.replace(",", "."))
                        ])

    return candidates


def _get_kraj(nr):
    for item in os.listdir("data"):
        if item.find("-"):
            fnr,name = item.split("-")
            fnr = int(fnr)

            if nr == fnr:
                return os.path.join("data", item)

def geocode_candidate(candidate, kname):

    nr, name, vek, party, aff, work, city, votes, votesp = candidate

    if city not in cities:
        resp = requests.get("https://nominatim.openstreetmap.org/search?q={city},{kname}&format=geojson".format(city=city, kname=kname))
        data = resp.json()
        if len(data["features"]) > 0:
            cities[kname][city] = data["features"][0]
        else:
            print("WARNING: {} {} {} {} not found".format(name, party, city, kname))
            cities[kname][city] = {"geometry":None}

    newcandidate = {
            "type":"Feature",
            "properties":{
                "nr":nr,
                "name": name,
                "vek": vek,
                "party": party,
                "aff": aff,
                "work": work,
                "city": city,
                "votes": votes,
                "votesp": votesp
            },
            "geometry": cities[kname][city]["geometry"]
    }

    return newcandidate


def geocode_kraj(kdata, kname, knr):

    candidates = []
    cities[kname] = {}
    for candidate in kdata:
        geocoded = geocode_candidate(candidate, kname)
        candidates.append(geocoded)

    candidates = {
            "type": "FeatureCollection",
            "features": candidates
    }

    with open(
            os.path.join("data", "mapy", str(knr)+".geojson"),
            "w") as mapa_out:
        json.dump(candidates, mapa_out, indent=4)




def main():

    with open("data/data/kraje.geojson") as kraje_file:
        data = json.load(kraje_file)
        for k in data["features"]:
            if k["properties"]["nr"] > 0:
                print("### {}".format(k["properties"]["Nazev"]))
                kdata = _parse_kraj(k["properties"]["nr"])
                geocode_kraj(kdata, k["properties"]["Nazev"], k["properties"]["nr"])




if __name__ == "__main__":
    main()

