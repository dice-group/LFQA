# Naïve-EAMT: Naïve Entity Aware Machine Translation Framework

This project aims to provide a configurable machine translation architecture. Through this architecture one could combine various implementations of Named Entity Recognition and Disambiguation tools with Neural Machine Translation to form an end-to-end entity aware machine translation RESTful service.

It comes already integrated with the following tools:

<!-- Table including all the integrated NER, EL and MT tools -->
<table id="comp-table">
    <thead>
        <tr>
            <th>Type</th>
            <th>Component</th>
            <th>ID</th>
            <th>Supported Lang.</th>
            <th>Link</th>
            <th>Maximum input sequence length</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan=4>NER</td>
            <td>Babelscape NER</td>
            <td>babelscape_ner</td>
            <td>de, en, es, fr, it, nl, pl, pt, ru</td>
            <td>https://huggingface.co/Babelscape/wikineural-multilingual-ner</td>
            <td>512 tokens (Based on BERT)</td>
        </tr>
        <tr>
            <td>Flair NER</td>
            <td>flair_ner</td>
            <td>de, en, es, nl</td>
            <td>https://github.com/flairNLP/flair</td>
            <td>512 tokens (Based on BERT)</td>
        </tr>
        <tr>
            <td>Davlan NER</td>
            <td>davlan_ner</td>
            <td>ar, de, en, es, fr, it, lv, nl, pt, zh</td>
            <td>https://huggingface.co/Davlan/bert-base-multilingual-cased-ner-hrl</td>
            <td>512 tokens (Based on mBERT)</td>
        </tr>
        <tr>
            <td>Spacy NER</td>
            <td>spacy_ner</td>
            <td>de, en, es, fr, it, nl, pl, pt, ru</td>
            <td>https://github.com/explosion/spacy-models/releases/tag/xx_ent_wiki_sm-3.4.0</td>
            <td>1 million character (spacy's default max_length) </td>
        </tr>
        <tr>
            <td rowspan=2>EL</td>
            <td>MAG</td>
            <td>mag_el</td>
            <td>en, de, fr, es, it, ja, nl</td>
            <td>https://github.com/dice-group/AGDISTIS/wiki/5---New-Capabilities---MAG</td>
            <td> </td>
        </tr>
        <tr>
            <td>mGenre</td>
            <td>mgenre_el</td>
            <td>Supports 105 languages (Table 10: https://arxiv.org/pdf/2103.12528.pdf)</td>
            <td>https://github.com/facebookresearch/GENRE</td>
            <td>512 tokens (Based on mBART)</td>
        </tr>
        <tr>
            <td rowspan=4>MT</td>
            <td>Libre Translate</td>
            <td>libre_mt</td>
            <td>ar, az, zh, cs, da, nl, en, eo, fi, fr, de, el, he, hi, hu, id, ga, it, ja, ko, fa, pl, pt, ru, sk, es, sv, tr, uk</td>
            <td>https://github.com/LibreTranslate/LibreTranslate</td>
            <td>512 tokens ()</td>
        </tr>
        <tr>
            <td>Opus MT*</td>
            <td>opus_mt</td>
            <td>Supports 203 languages for translation to English (https://opus.nlpl.eu/Opus-MT/)</td>
            <td>https://github.com/Helsinki-NLP/Opus-MT</td>
            <td>512 tokens (https://huggingface.co/Helsinki-NLP)</td>
        </tr>
        <tr>
            <td>NLLB MT**</td>
            <td>nllb_mt</td>
            <td>Supports 196 languages</td>
            <td>https://github.com/facebookresearch/fairseq/tree/nllb/#multilingual-translation-models</td>
            <td> </td>
        </tr>
        <tr>
            <td>MBart MT**</td>
            <td>mbart_mt</td>
            <td>Supports 53 languages</td>
            <td>https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt</td>
            <td>mBART - 512 tokens, mBART50 - 1024 tokens (https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt)</td>
        </tr>
    </tbody>
</table>

Language code ref: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes 

[*] currently the application only downloads some (de, es, fr, nl, ru) of the supported languages' data for Opus MT. For further language support, please download the data and modify the [configuration](helsinki_opusmt_services.json). This should be done before [setup](setup_data.sh) is executed, otherwise you will have to rebuild the Opus docker image with the right configuration.

[**] for NLLB and MBart MT, currently the application only allows the following: de, es, fr, pt, ru. Edit the ```lang_code_map``` in the component file to extend support for further languages.
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

Before running the setup script, please make sure you have the proper docker permissions. You can test it using the following command (without sudo):

```docker run hello-world```

If that works, then you can proceed normally, otherwise, you must perform the steps to [manage docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

Also, please make sure that your ```docker-compose``` is version 1.28.0 or above to support [docker profiles](https://docs.docker.com/compose/profiles/).

Download and setup the data using the following command (needs 150GB free storage, can take a few hours to finish):

```./setup_data.sh```

Then, build the docker image:

```docker build -t naive-eamt .```

Finally, to start use the start script:

```./start_docker_containers.sh```

To stop, use the stop script:

```./stop_docker_containers.sh```

### Logs
The logs are maintained in the ```logs/neamt.log``` file

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

__Optional Parameters__: The NEAMT application also allows its users to configure two optional parameters: 
- *target_lang* (default: **en**): language code (e.g en, de, fr etc.) for the target language for the machine translation
- *placeholder* (default: **00**): string value that will be used as a placeholder in concatenation with a number
- *replace_before* (default: **False**): boolean value, if set to True, the application will replace placeholders with target labels before sending for machine translation

Sample query with optional parameters:
```bash
curl --location --request POST 'http://porque.cs.upb.de:6100/custom-pipeline' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'components=babelscape_ner, mgenre_el, libre_mt' \
--data-urlencode 'query=Wer ist älter, Lionel Messi oder Christiano Ronaldo?' \
--data-urlencode 'placeholder=wd:res' \
--data-urlencode 'replace_before=False' \
--data-urlencode 'target_lang=ru'
```
## Customized Components
### Component I/O Formatting
<a id="NER">__NER__:</a> For the components that strictly perform the task of named entity recognition, the expected input is a dictionary containing text in natural language (en,de,fr,es). The output should be a dictionary containing the string and information of annotated entities. Following is an example:

*Input*: 
```json
{
  "text": "Ist Hawaii der Geburtsort von Obama?"
}
```


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

<a id="EL">__EL__:</a> For the components performing only the entity linking task, the expected input is the output from the [*NER*](#NER). The output should be the same dictionary with additional information about the entity mentions. Carrying on with the example from above, following is a sample output:

*Output*: 
```json
{
  "text": "Ist Hawaii der Geburtsort von Obama?",
  "lang": "de",
  "kb": "wd",
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

Additionally, you can make use of the functions in [placeholder_util.py](util/placeholder_util.py) to replace the entities with placeholder tokens and vice versa. The framework also provides dummy NER([no_ner](component/empty_ner.py)) and EL([no_el](component/empty_el.py))  components that would format the data according to the listed I/O format but would not perform any NER/EL tasks. The dummy components can be used to build MT only pipelines.

__Combination__: If your custom component is a combination of consecutive components in the pipeline, then you must follow the input/output format accordingly. Your combined component must comply to the input format for the point of entrance and output format for the point of exit.
<!-- Obsolete: Provide the link to sample code (LibreMT) -->
<!-- If in case the combination of your components do not need any intermediatory processing of the input or outputs you can set the ```skip_intermediate_processing``` to ```False``` as demonstrated here: *This is a placeholder for the link* -->



### How to add a new component?

To add your own custom component you can follow these steps:
- Add your dependencies to [requirements.txt](requirements.txt)
- Create a new python file in the ```component/``` directory
- Your python file must have a ``` process_input``` function that will receive the input as per its placement in the pipeline ([I/O Formatting](#component-io-formatting))
- Make sure to load the necessary resources (models, data etc.) onto the memory only inside the ```__init__``` function, this helps keeps the application memory efficient
- Import your component in the [start.py](start.py) and add an ID to Class mapping inside ```comp_map```
- Create a new pipeline with your component in [configuration.ini](configuration.ini)

Additional steps for Docker based components:
- If your component has a docker image, then create a service using your docker image in [docker-compose.yml](docker-compose.yml)
- Assign a new docker profile to your component to ensure that it's not loaded unnecessarily
- Modify the logic in [find_profiles.py](find_profiles.py) to accommodate your component

### How to pass a custom parameter as input?

By default the framework passes on all the extra parameters in the input to the components. However, one has to make sure the that custom parameter name does match the preexisting parameters. To avoid conflict with the existing parameters, it would be a good practice to add a custom prefix to your parameter (e.g <b>orgname_</b>custompara1).
