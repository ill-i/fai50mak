"""
This is a DaCHS processor (http://docs.g-vo.org/DaCHS/processors.html)
to add standard headers to FITS files from the FAI 50cm Maksutov telescope.
"""

import csv
import glob
import os
import re

from gavo.helpers import fitstricks
from gavo import api

class PAHeaderAdder(api.HeaderProcessor):

  def _createAuxiliaries(self, dd):
    logs_dir = os.path.join(
      dd.rd.resdir, "logbook")
    recs = []

    for src_f in glob.glob(logs_dir+"/*.csv"):
      with open(src_f, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        desired_keys = dict(
          (n, (n or "EMPTY").split()[0]) for n in rdr.fieldnames)
        source_key = os.path.basename(src_f).split(".")[0]

        for rec in rdr:
          new_rec = {
            "source-file": source_key}
          for k, v in rec.items():
            new_key = desired_keys[k]
            if new_key=="Идентификационный":
              new_key = "ID"
            new_rec[new_key] = v
          recs.append(new_rec)

    self.platemeta = dict(
      (rec["ID"], rec) for rec in recs)

  def _isProcessed(self, srcName):
    return os.path.exists(srcName+".hdr")

  def _mungeHeader(self, srcName, hdr):
    plateid = srcName.split(".")[-2].split("_")[-1]
    thismeta = self.platemeta[plateid]

		#group 2
		#coords orig

    mat = re.match(r"(\d\d)h(\d\d)m$", thismeta["RA"])
    formatted_ra = "{}:{}".format(mat.group(1), mat.group(2))
    mat = re.match(r"(\d\d)\.(\d\d)$", thismeta["DEC"])
    formatted_dec = "{}:{}".format(mat.group(1), mat.group(2))
    cleaned_object = re.sub("[^ -~]+", "", thismeta["OBJECT"])

		#date orig

		#time start

		#time end

		#obj type

		#exptimen
		exp = thismeta["EXPTIME"]
		#numexp

		#observat
		observatory = "Fesenkov Astrophysical Institute"

		#sitename
		sitename = "https://www.fai.kz"

		sitelong = 43.17667
		sitelat = 76.96611
		siteelev = 1450

		#telescope
		tel_dict = {"50cm менисковый телескоп Максутова":"Wide aperture Maksutov meniscus telescope with main mirror 50 cm" "Большой Шмидт": "Schmidt telescope (large camera)"}
		if thismeta["TELESCOPE"] == thismeta["TELESCOPE"]:
			telescope = tel_dict[thismeta["TELESCOPE"]]
		else:
			telescope = "unknown"

		#foclen
		foclen_dic = {"Wide aperture Maksutov meniscus telescope with main mirror 50 cm":1.2,"Schmidt telescope (large camera)":0.773,"Schmidt telescope (small camera)":0.17, "unknown":0}
		foclen = foclen_dic[telescope]
		
		#observer
		observers_dict = {'Рожковский Д.А.': 'Rozhkovskij D.A.', 'Торопова Т.П.':'Tropova T.P.', 
                  'Городецкий Д.И.':'Gordetskij D.I.', 'Глушков Ю.И.':'Glushkovskij Yu.I.','Торопова Т.П.  Рожковский Д.А.': 'Tropova T.P., Rozhkovskij D.A.',
                  'Рожковский Д.А., Торопова Т.П.' : 'Rozhkovskij D.A., Tropova T.P.', 'Рожковский Д.А., Павлова Л.А.' : 'Rozhkovskij D.A., Pavlova L.A.',
                  'Карягина З.В.':'Karyagina Z.V.', 'Матягин В.С.': 'Matyagin V.S.', 'Павлова Л.А':'Pavlova L.A.', 'Гаврилов':'Gavrilov', 
                  'Курчаков А.В.':'Kurchakov A.V.','Рожковский Д.А.   Городецкий Д.И.':'Rozhkovskij D.A.   Gordetskij D.I.','Солодовников В.В.':'Solodovnikov V.V.'}

			observer = observers_dict[thismeta["OBSERVER"]]


      return fitstricks.makeHeaderFromTemplate(
      fitstricks.WFPDB_TEMPLATE,
      originalHeader=hdr,
      RA_ORIG=formatted_ra,
      DEC_ORIG=formatted_dec,
#      OBSERVER=thismeta["OBSERVER"],
      OBJECT=cleaned_object,
      ORIGIN="Contant")


if __name__=="__main__":
  api.procmain(PAHeaderAdder, "fai50mak/q", "import")