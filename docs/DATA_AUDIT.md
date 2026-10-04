# Climate and soil data audit

Audited on 4 October 2026. Period: **1 January 2005–31 December 2025**.

**Both Kyabram and Kununurra Aero provide usable climate inputs.** Kyabram has a modest advantage in observed rainfall and temperature coverage. This screening does not establish a large overall quality difference or independently validate the observations.

| Check | Kyabram 080091 | Kununurra Aero 002056 |
|---|---:|---:|
| Daily records | 7,670 | 7,670 |
| Missing dates | 0 | 0 |
| Duplicate dates | 0 | 0 |
| Official observed rainfall | 98.5919% | 97.6923% |
| Official observed maximum temperature | 99.4263% | 98.5919% |
| Official observed minimum temperature | 99.3611% | 98.6701% |
| Long-term-average radiation estimates | 13 days | 0 days |

“Observed” means SILO source code 0. Remaining rainfall includes interpolated and deaccumulated values; a complete series is not necessarily fully observed. Reference evapotranspiration is calculated, not measured maize water use.

## Findings that affect the location choice

- **Use Kununurra Aero (002056) for the WA option.** The separately downloaded Kununurra record (002038) contains entirely interpolated rainfall and temperatures during this period.
- Kyabram has 13 long-term-average radiation estimates, which matter because radiation contributes to derived evapotranspiration.
- Longest consecutive non-code-0 rainfall runs: 30 days at Kyabram and 12 at Kununurra Aero. Vapour-pressure runs: 10 and 101 days respectively.
- Both climate datasets passed the checked date, missing-value, sentinel-value, nonnegative-input and minimum/maximum-temperature consistency checks. No new imputation or clipping was applied.
- All ten small soil-water-capacity subsets downloaded and contained valid values at five depths down to one metre. **These are station-area access checks, including an airport location, not final agricultural-field soil parameters.**

## Recommendation and remaining work

Kyabram remains the easier starting point because of the identified local maize and FAO-56 research. **Kununurra Aero is a defensible WA option; climate completeness does not justify rejecting it.** The final location has not been locked.

Before building the shared environment, select an agricultural field coordinate and verify native-resolution soil parameters, root depth, drainage assumptions, local growing-season dates and crop coefficients. Preserve climate source flags and keep whole seasons together in training, validation and test splits.

## Data and reproduction

Download and extract [Irrigation_Data_Audit.zip](../data/Irrigation_Data_Audit.zip). It contains the unmodified climate downloads, selected daily data in JSON, soil GeoTIFF screening subsets, source metadata, detailed audit outputs and scripts.

Inside the extracted `irrigation_audit` directory:

```bash
python audit.py
python audit_soil.py
```

The climate audit uses Python's standard library. The soil audit requires Pillow. The download scripts are included; climate refreshes require an authorised `SILO_EMAIL` environment variable. No user's email is embedded in the package. A fresh download may include source revisions.

Detailed results are also readable directly:
- [Climate audit JSON](climate_audit.json)
- [Soil audit JSON](soil_audit.json)

## Full audit notes

```text
IRRIGATION DATA AUDIT — 4 OCTOBER 2026

Decision
Both Kyabram and Kununurra Aero provide usable climate inputs for a research
prototype. Kyabram has a modest advantage in observed rainfall and temperature
coverage; the audit does not establish a large overall quality difference.
Kyabram remains the easier starting point because of the identified local
maize/FAO-56 studies. WA is a defensible choice if local relevance is preferred.
For WA use Kununurra Aero 002056, not Kununurra 002038, for these years.

Scope and provenance
Downloaded SILO Patched Point 'alldata' records, 2005-01-01 through 2025-12-31
inclusive (21 complete calendar years), for stations 080091, 002056 and 002038.
Raw files retain SILO's headers, licence and source codes. The first dummy
1997 row is a format demonstration and was excluded, as the file instructs.
There are 7,670 expected daily records, including five leap days, per station.
The daily JSON files preserve values in the selected input columns without
imputation, clipping or removal. Full unmodified responses remain in raw/.

Observed coverage (SILO code 0; denominator 7,670 days)
Variable                Kyabram 080091    Kununurra Aero 002056
Rainfall                98.5919%          97.6923%
Maximum temperature     99.4263%          98.5919%
Minimum temperature     99.3611%          98.6701%
Vapour pressure         99.3611%          97.6923%

Both series passed the checked structural/numerical conditions: exact date
coverage, chronological order, no duplicates, no malformed rows, no nonfinite
values, no selected sentinel values, no minimum temperature above maximum,
and no negative rainfall, ETo, radiation or vapour pressure.
These checks do not prove every observation is accurate. Extreme values were
retained, not automatically 'corrected'. There was no independent station
validation or recalculation of SILO reference evapotranspiration.

Important qualifications
1. Complete SILO records include estimates. Kyabram rain includes 85 daily
interpolations and 23 deaccumulated records; Aero includes 165 interpolations
and 12 deaccumulated records. These are not all direct 24-hour observations.
2. Kununurra 002038 has 0% code-0 observations for rainfall, temperatures and
vapour pressure during this period: all are code 25. This is the key reason
not to choose a weather station from its town name alone.
3. Radiation is mostly satellite-derived (code 42), not ground-station
observations. Kyabram has 13 code-75 long-term-average radiation estimates;
Aero has none. Both have 18 code-25 radiation estimates. Kyabram code-75 dates:
2005-12-05, 2005-12-14, 2006-01-02, 2006-01-03, 2006-01-07, 2006-01-08,
2008-01-07, 2008-01-08, 2009-01-02, 2013-12-24, 2013-12-29, 2013-12-30,
2013-12-31. Radiation affects derived ETo, so retain these provenance flags.
4. Longest consecutive runs without code-0 rainfall: Kyabram 30 days, Aero
12 days. Vapour pressure: Kyabram 10 days, Aero 101 days. The detailed JSON
includes yearly coverage to make these gaps visible.
5. ETo is calculated reference evapotranspiration (mm/day), not measured maize
water use. A crop coefficient and a justified stress model are still needed.
6. The November–March and April–September summaries in the audit are calendar
screening windows only. They do not establish local maize planting schedules.
7. No new missing-value filling or smoothing was applied during this audit.

Soil access and numerical screening
Downloaded SLGA Available Volumetric Water Capacity (AWC) v2 WCS subsets for
five depths: 0–5, 5–15, 15–30, 30–60 and 60–100 cm, around the two comparison
weather stations. All 10 small subsets contained six valid cells and zero
NoData cells. Kyabram samples ranged from 9–13% AWC; Aero from 11–14%.
This demonstrates accessible numerical data, not superior soil-model accuracy.

These station-coordinate subsets include an airport area for Kununurra; they
are NOT approved agricultural-field soil parameters. WCS returned small
service-generated grids, not a guaranteed native-pixel extraction. A final
field location needs native-resolution sampling, soil depth, drained upper
limit/lower limit, uncertainty estimates and rooting-depth checks. We did not
compute or approve root-zone storage from these screening samples. AWC alone
does not specify saturation or drainage behaviour. Soil values are spatial
model predictions, not field measurements. Earlier ASRIS access failed; the
current TERN AWC v2 service succeeded. No substitute soil values were invented.

Recommended next steps
Select Kyabram for the simpler evidence-backed maize setup, or Kununurra Aero
if WA relevance is a priority. There is no climate completeness reason to
reject WA. Choose an actual agricultural coordinate, confirm local growing
season/crop parameters, retain provenance flags and fix whole-season splits.
Use historical rainfall/ETo available before the action in observations;
same-day realised weather can drive the transition without being revealed
as a perfect forecast. Do not select final test years to favour an agent.
The notebook, agent settings and GitHub setup are separate pending tasks.

Reproduction
python audit.py
This uses Python's standard library and recreates the daily JSON and audit.
python audit_soil.py
This uses Pillow to inspect the downloaded GeoTIFF subsets.
To refresh climate downloads, set SILO_EMAIL to an authorised email and run
python download_climate.py. The authorised user's email is not embedded in
this package. Downloading again may retrieve revised SILO data.
python download_soil.py retrieves the small soil screening subsets.
SHA-256 hashes are recorded for downloaded climate and soil data.

Sources and attribution
Climate: Queensland Government SILO, constructed from Bureau of Meteorology
and other supplier data; CC BY 4.0. Raw headers retained.
https://www.longpaddock.qld.gov.au/silo/
https://www.longpaddock.qld.gov.au/silo/api-documentation/reference/
https://www.longpaddock.qld.gov.au/silo/about/about-data/
https://www.longpaddock.qld.gov.au/silo/faq/
Soil: Searle, R., Nimalka Somarathna, P. & Malone, B. (2023), Soil and Landscape
Grid National Soil Attribute Maps – Available Volumetric Water Capacity
(Percent), Version 2.0, TERN, DOI 10.25919/4jwj-na34; CC BY 4.0.
https://portal.tern.org.au/metadata/482301c2-b9a1-4345-b142-815f9b37890a
https://data.tern.org.au/model-derived/slga/NationalMaps/SoilAndLandscapeGrid/AWC/v2/
Context supporting Kyabram model development (not validation of our model):
https://agriculture.vic.gov.au/farm-management/water/irrigation/variation-in-irrigation-requirements-of-forages-northvic
```
