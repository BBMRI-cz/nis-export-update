# Architecture Overview

This service synchronizes patient-related data from multiple source systems into the data catalogue.

At a high level:
- each source system exposes its own API,
- the sync job calls those APIs,
- it aggregates source data into one patient-level record,
- and upserts that record to the catalogue.

```mermaid
flowchart LR
    subgraph sourceSystems [Source Systems]
        Biobank[("Biobank")]
        Radiology[("Radiology")]
        Sequencing[("Sequencing")]
        WsiSlides[("WSI / Slides")]
    end

    subgraph sourceApis [Source APIs]
        BiobankApi["Biobank API"]
        RadiologyApi["Radiology API"]
        SequencingApi["Sequencing API"]
        WsiApi["WSI API"]
    end

    Biobank --- BiobankApi
    Radiology --- RadiologyApi
    Sequencing --- SequencingApi
    WsiSlides --- WsiApi

    SyncJob["Sync Job: aggregate per patient"]

    BiobankApi --> SyncJob
    RadiologyApi --> SyncJob
    SequencingApi --> SyncJob
    WsiApi --> SyncJob

    SyncJob -->|"upsert aggregated patient"| CatalogueApi["Data Catalogue API"]
    CatalogueApi --> Catalogue[("Data Catalogue")]
```

In one sentence: for each patient, the sync job reads from all source APIs, aggregates the data into one coherent record, and uploads it into the data catalogue.
