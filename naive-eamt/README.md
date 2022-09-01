# Naïve-EAMT: Naïve Entity Aware Machine Translation Framework

This project aims to provide a configurable machine translation architecture. Through this architecture one could combine various implementations of Named Entity Recognition and Disambiguation tools with Neural Machine Translation to form an end-to-end entity aware machine translation RESTful service.

It comes already integrated with the following tools:

<!-- Table including all the integrated NER, EL and MT tools -->
<table id="comp-table">
    <thead>
        <tr>
            <td>Type</td>
            <td>Component</td>
            <td>ID</td>
            <td>Link</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan=4>NER</td>
            <td>Babelscape NER</td>
            <td>babelscape_ner</td>
            <td>https://huggingface.co/Babelscape/wikineural-multilingual-ner</td>
        </tr>
        <tr>
            <td>Flair NER</td>
            <td>flair_ner</td>
            <td>https://github.com/flairNLP/flair</td>
        </tr>
        <tr>
            <td>Davlan NER</td>
            <td>davlan_ner</td>
            <td>https://huggingface.co/Davlan/bert-base-multilingual-cased-ner-hrl</td>
        </tr>
        <tr>
            <td>Spacy NER</td>
            <td>spacy_ner</td>
            <td>https://spacy.io/api/entityrecognizer</td>
        </tr>
        <tr>
            <td rowspan=2>EL</td>
            <td>MAG</td>
            <td>mag_el</td>
            <td>https://github.com/dice-group/AGDISTIS/wiki/5---New-Capabilities---MAG</td>
        </tr>
        <tr>
            <td>mGenre</td>
            <td>mgenre_el</td>
            <td>https://github.com/facebookresearch/GENRE</td>
        </tr>
        <tr>
            <td rowspan=2>MT</td>
            <td>Libre Translate</td>
            <td>libre_mt</td>
            <td>https://github.com/LibreTranslate/LibreTranslate</td>
        </tr>
        <tr>
            <td>Opus MT</td>
            <td>opus_mt</td>
            <td>https://github.com/Helsinki-NLP/Opus-MT</td>
        </tr>
    </tbody>
</table>

<!-- ## Normal Setup
We recommend using a tool like Anaconda to create a separate environment for this project's dependencies.

You can create a python environment for this project using the following command:

```conda create -n lf_eamt python=3.9```

Once the environment is created, you can activate it using:

```conda activate lf_eamt```

Afterwards, to install the dependencies and the download the needed files, run:

```bash req_install.sh``` -->

## Configuration

The application uses a configuration file [```configuration.ini```](configuration.ini) to allow users to form pipelines based upon their combination of components.

A sample pipeline configuration would look like this:
```ini
# unique pipeline section title
[EAMT Pipeline 2]
# pipeline name (can be non-unique as well)
name = babelscape-mgenre-libre
# ordered list of component ids in the pipeline
components = ["babelscape_ner", "mgenre_el", "libre_mt"]
# Path name (without /) that will be used to query this pipeline at localhost:6100/<path>
path = pipeline_bmgl
```

The pipeline config allows to join any existing components together as long as they follow [I/O formatting rules](#NER). 
The component IDs can be found in the [table above](#comp-table).

__Important__: The application only initiates the components mentioned in the config pipelines to be memory efficient. To save on memory, please comment out the config for the non-required pipelines.

## Docker Setup
First, download and setup the data using the following command (needs 150GB free storage, can take a few hours to finish):

```bash setup_data.sh```

Then, build the docker image:

```docker build -t naive-eamt .```

Finally, to start use the start script:

```bash start_docker_containers.sh```

To stop, use the stop script:

```bash stop_docker_containers.sh```

### Logs
The logs are maintained in the ```log/neamt.log``` file

### Query
The configured pipelines can be queried through HTTP POST request, like:
```bash
curl --location --request POST 'http://localhost:6100/pipeline_bmgo' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'query=Ist Hawaii der Geburtsort von Obama'
```
The output format would depend upon the last component in the queried pipeline.

The application also accepts custom pipelines submitted along with the HTTP request. However, the components must be pre-initialized.

The query with custom pipeline request would look something like this:
```bash
curl --location --request GET 'http://localhost:6100/custom-pipeline' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'query=Ist Hawaii der Geburtsort von Obama' \
--data-urlencode 'components=spacy_ner, mag_el, opus_mt'
```
## Customized Components
### Component I/O Formatting
<a id="NER">__NER__:</a> For the components that strictly perform the task of named entity recognition, the expected input is a string containing text in natural language (en,de,fr,es). The output should be a JSON containing the string and information of annotated entities. Following is an example:

*Input*: ```Ist Hawaii der Geburtsort von Obama?```


*Output*: 
```json
{
  "text": "Ist Hawaii der Geburtsort von Obama?",
  "lang": "de",
  "ent_mentions": [
      {
          "start": 4,
          "end": 10,
          "surface_form": "Hawaii"
      },
      {
          "start": 30,
          "end": 35,
          "surface_form": "Obama"
      }
  ]
}
```

<a id="EL">__EL__:</a> For the components performing only the entity linking task, the expected input is the output from the [*NER*](#NER). The output should be the same JSON with additional information about the entity mentions. Carrying on with the example from above, following is a sample output:

*Output*: 
```json
{
  "text": "Ist Hawaii der Geburtsort von Obama?",
  "lang": "de",
  "ent_mentions": [
      {
          "start": 3,
          "end": 9,
          "surface_form": "Hawaii",
          "link": "Q68740"
      },
      {
          "start": 29,
          "end": 34,
          "surface_form": "Obama",
          "link": "Q76"
      }
  ]
}
```

<!-- __MT__: For the components performing the machine translation task, the expected input is a string containing text in natural language but with entities replaced using a __\[PLACEHOLDER_N\]__ . The expected output is the translated string in English alongwith with placeholder token in the relevant position. Following is an example:

*Input*: ```Ist [PLACEHOLDER_1] der Geburtsort von [PLACEHOLDER_2]?```


*Output*: ```Is [PLACEHOLDER_1] the birth place of [PLACEHOLDER_2]?```
-->

__MT__: For the components performing the machine translation task, the expected input is the output from [*EL*](#EL) task. The output is the translated natural language text in English.

*Output*: ```Is Hawaii the birth place of Barack Obama?```

Additionally, you can make use of the functions in [placeholder_util.py](util/placeholder_util.py) replace entities with placeholder tokens and vice versa.

__Combination__: If your custom component is a combination of consecutive components in the pipeline, then you must follow the input/output format accordingly. Your combined component must comply to the input format for the point of entrance and output format for the point of exit.
<!-- Obsolete: Provide the link to sample code (LibreMT) -->
<!-- If in case the combination of your components do not need any intermediatory processing of the input or outputs you can set the ```skip_intermediate_processing``` to ```False``` as demonstrated here: *This is a placeholder for the link* -->