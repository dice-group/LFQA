# Naïve-EAMT: Naïve Entity Aware Machine Translation Framework

This project aims to provide a configurable machine translation architecture. Through this architecture one could combine various implementations of Named Entity Recognition and Disambiguation tools with Neural Machine Translation to form an end-to-end entity aware machine translation RESTful service.

It comes already integrated with the following tools:

<!-- Table including all the integrated NER, EL and MT tools -->
*There will a table here instead of this text, soon.*

<!-- ## Normal Setup
We recommend using a tool like Anaconda to create a separate environment for this project's dependencies.

You can create a python environment for this project using the following command:

```conda create -n lf_eamt python=3.9```

Once the environment is created, you can activate it using:

```conda activate lf_eamt```

Afterwards, to install the dependencies and the download the needed files, run:

```bash req_install.sh``` -->

## Docker Setup

*To be updated*

### Component I/O Formatting
<a name="NER"> __NER__: </a> For the components that strictly perform the task of named entity recognition, the expected input is a string containing text in natural language (en,de,fr,es). The output should be a JSON containing the string and information of annotated entities. Following is an example:

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

__EL__: For the components performing only the entity linking task, the expected input is the output from the [*NER*](#NER). The output should be the same JSON with additional information about the entity mentions. Carrying on with the example from above, following is a sample output:

*Output*: 
```json
{
  "text": "Ist Hawaii der Geburtsort von Obama?",
  "lang": "en",
  "ent_mentions": [
      {
          "start": 3,
          "end": 9,
          "surface_form": "Hawaii",
          "link": 'Q68740'
      },
      {
          "start": 29,
          "end": 34,
          "surface_form": "Obama"
          "link": 'Q76'
      }
  ]
}
```

__MT__: For the components performing the machine translation task, the expected input is a string containing text in natural language but with entities replaced using a __\[PLACEHOLDER_N\]__ . The expected output is the translated string in English alongwith with placeholder token in the relevant position. Following is an example:

*Input*: ```Ist [PLACEHOLDER_1] der Geburtsort von [PLACEHOLDER_2]?```


*Output*: ```Is [PLACEHOLDER_1] the birth place of [PLACEHOLDER_2]?```

__Combination__: If your custom component is a combination of consecutive components in the pipeline, then you must follow the input/output format accordingly. Your combined component must comply to the input format for the point of entrance and output format for the point of exit.
<!-- TODO: Provide the link to sample code (LibreMT) -->
If in case the combination of your components do not need any intermediatory processing of the input or outputs you can set the ```skip_intermediate_processing``` to ```False``` as demonstrated here: *This is a placeholder for the link*