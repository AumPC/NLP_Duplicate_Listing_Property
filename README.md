# NLP Duplicate Listing Property
An NLP project: Detect duplication of property in condo listings
- Query Data From Postgresql
- Extract Information
- Filter Data
- Similarity Data
- Scoring

# Installation
`pip install -r requirements.txt`

- Require own database which describe in *parameter_nlp_db.json*.
- Require global database which describe in *parameter_main_db.json*.


# Run Module
`flask run --reload`

Will be running on http://127.0.0.1:5000/

# API
Almost api use **POST** method.
## /clone
Clone database with preprocessing data.
Return multiple rows and mismatch rows in JSON format.

**This api will not generate or reset parameter.json.**

This also can be used by command line. Response will be printed when finish.

```python clone.py```

## /update/\<row_id>
Upsert a row into database with preprocessing data.
Return multiple rows and mismatch rows (if found) in JSON format.

## /check/\<row_id>
Calculate duplicate score with all rows in same project,
and split to 3 groups by threshold.
If requested row's project is null,
system will calculate with all rows which their project is null.
Return scores, multiple rows and mismatch rows (if found) in JSON format.

**Must update requested row into database first**

## /check/request
Work like previous api but receive JSON body format instead of row's id.
This api also preprocess requested data automatically.
Requested body format must follow the example.
**project** and **price** field is not required.
If not defined, system will calculate them as null value.
Return scores, multiple rows and mismatch rows (if found) in JSON format.


```
{
	"id": 12345,
	"project": 12345,
	"title": "some title",
	"price": [100, 100],
	"size": 55,
	"tower": "some tower",
	"floor": "20",
	"bedroom": "1",
	"bathroom": "1",
	"detail": "some detail (can have html tag)"
}
```

## /check/all
Original feature, query **Main** database's all row, preprocess, calculate score and group results.
Unlike previous two, strong and medium duplicate document will be summed into groups by consider maximum (pair) score.
Return group of strong, medium group of duplicate, weak pair, multiple rows and mismatch rows in JSON format.

**If enable auto_threshold in parameter.json, new threshold will be calculated before split group**

This also can be used by command line. Response will be printed when finish.

```python check_all.py```

## /parameter
This api can receive **GET** method, return parameter.json's value.

Set new value in requested body to parameter.json.
Requested body can be JSON which consist of want-to-set key-value.
Return 'success' if success.

## /parameter/reset
Reset parameter.json to default value.
**Default value may not fit to data well**

# Parameter and Scoring
*This is brief description*

**weight** field in parameter.json will be used as weight for calculate *FIELD_SCORE* by Levenshtein distance and different percentage of each field of record.
Summation of all field in **weight** must equal 1.

Record detail difference will be calculated with jaccard index, let's name it *DETAIL_SCORE*.

Finally, *FIELD_SCORE* and *DETAIL_SCORE* will be calculated to *TOTAL_SCORE* by weight sum, this weight is controlled by **half_weight_frequency** parameter.

**half_weight_frequency** means number of words in detail that make this final weight equal 0.5, *DETAIL_SCORE* will gain weight higher if record's detail is longer.

# Parameter and Threshold
**strong_threshold**, **medium_threshold** and **weak_threshold** is minimum score to consider record as member of duplicate group.
These parameter can be defined manually, or automatically calculated by set **auto_threshold** to *true*.

In case of using **auto_threshold**, there will be 2 more parameter that can be set.
First, **strong_threshold** will come from score that made all higher-score record pair is duplicate confidently by compare first 100 letters of detail and title as string.
All score will be divided to intervals. Number of intervals is defined by **data_range** parameter.
**medium_threshold** is threshold between 2 intervals which highest slope appear.
Last, **weak_threshold** is calculated from last N percentile of data (from highest score), N is defined by **tail_percentile** parameter.