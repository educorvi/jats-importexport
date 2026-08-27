# Front

Represents a JATS <front> element containing article metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**journal_id** | **str** |  | 
**journal_title** | **str** |  | 
**journal_subtitle** | **str** |  | 
**issn** | **str** |  | 
**publisher_name** | **str** |  | 
**publisher_institution** | **str** |  | 
**publisher_addr_line** | **str** |  | 
**publisher_postal_code** | **str** |  | 
**publisher_city** | **str** |  | 
**publisher_phone** | **str** |  | 
**publisher_email** | **str** |  | 
**publisher_uri** | **str** |  | 
**article_id** | **str** |  | 
**title** | **str** |  | 
**article_subtitle** | **List[str]** |  | 
**author_surname** | **str** |  | 
**co_author_surname** | **str** |  | 
**co_author_aff** | **str** |  | 
**self_uri** | **str** |  | 
**article_categories** | **str** |  | 
**pub_date_ausgabedatum** | **date** |  | 
**pub_date_aktualisierte_fassung** | **date** |  | 
**history_initial_publication** | **str** |  | 
**history_correction** | **str** |  | 
**history_latest_version** | **str** |  | 
**copyright_statement** | **str** |  | 
**copyright_holder** | **str** |  | 
**abstract_short_title** | **str** |  | 
**abstract_short** | **str** |  | 
**abstract_summary_title** | **str** |  | 
**abstract_summary** | **str** |  | 
**keywords** | **List[str]** |  | 
**beschreibender_typ** | **str** |  | 
**bisherige_bestellnummer** | **str** |  | 
**webcode** | **str** |  | 
**organisationseinheit** | **str** |  | 
**fachbereich** | **str** |  | 
**sachgebiet** | **str** |  | 
**veroeffentlichungsstatus** | **str** |  | 
**bildnachweis** | **str** |  | 
**ueberschriften_mit_nummerierung** | **bool** |  | 

## Example

```python
from jats_importexport_client.models.front import Front

# TODO update the JSON string below
json = "{}"
# create an instance of Front from a JSON string
front_instance = Front.from_json(json)
# print the JSON string representation of the object
print(Front.to_json())

# convert the object into a dict
front_dict = front_instance.to_dict()
# create an instance of Front from a dict
front_from_dict = Front.from_dict(front_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


