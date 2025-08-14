
<!-- TOC -->
  * [Data Formats](#data-formats)
    * [Simple Types](#simple-types)
      * [Date](#date)
<!-- TOC -->

# CSAF: Common Security Advisory Framework Version

## Introduction
* CSAF 2.0 support 
* JSON is the only CSAF-compliant format
* Specification available [here](https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html#)

This implementation does not aim to be complete, since the specification allows for *many*
    options we yet to have observe any vendor of relevance using them.

Further, since every vendor populates CSAFs slightly differently, this implementation only aims to provide nice
retrieval interfaces of information and no true interpretation. For some uses cases and vendors, this makes
retrieving the actually necessary information almost trivially easy, for others it becomes a project of its own.
For example uses of this implementation, I refer to the `notus-generator` repository.

## Core Components
A CSAF document contains 4 core components:
* `document` (publisher, references, tracking, ...): Metadata
* `product_tree` (specification of individual Software/OS/Hardware components, their versions etc. and providing of explicit unique IDs in this document): Technically optional, but most commonly used
* `relationships` (Forest data structure with products from the `product_tree` in the root and leaves.): Technically optional, usage varies
* `vulnerabilities` (Which CVE + Score + which components are affected/ what remediations (if any) exist or are planned.)

Usage of the `product_tree` must carefully consider (i) the forest's height it is encoded as and how the branches the vendor is using at each height interplay (ii) Whether any explicit version data encoded is actually CSAF compliant (many vendors/publishers are *not* CSAF compliant in those fields.).
Several known vendors do not follow the following guideline of the CSAF specification:
> It is recommended to use the hierarchical structure of vendor -> product_name -> product_version whenever possible to support the identification and matching of products on the consumer side.

For certain methods, the `Csaf` class assumes a tree of height 2, i.e., that the CSAF follows the above recommendation.


<br>
Usage fo the `relationships` must carefully consider whether it has height > 1 (i.e., any nodes and not just root and leaf nodes). It that case, transitive remapping of the relationships during usage may be necessary.

Usage of `vulnerabilities` must carefully consider (i) whether the IDs referred to are only from the `product_tree` or from the `relationships`, (ii) what the remediation status of the resp. affected products is.
Further, a CSAF may simple explicitly document that _none_ of the listed products are vulnerable to a given CVE.



## Data Formats


### Primitive Types
Almost all primitive values in the JSON are `strings`. I.e., even if a uses numeric identifiers, he encodes them as strings.
As a result `['0']` may commonly exist (and thus evaluates to `True`), but `[0]` (evaluating to `False`) could never be a correct encoding for such identifiers.

### Simple Types
#### Date
* {YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}Z
* Example: 2024-10-08T00:00:00Z


### Product Identification Helpers
To ease exact identification of a given product, a vendor  *may* add the `product_identification_helper`
field and populate with one or more CPEs, PURLs, Model Numbers, SBOM URLs, Hashes, etc.
Note: Do not assume that the vendor is compliant in how they populate these field. 
At least for one vendor we are aware that the CPE values they provide are not following the CPE specification when compared to "what the vendor means".
Similar non-compliancy occurrence holds true for, e.g., version fields.
