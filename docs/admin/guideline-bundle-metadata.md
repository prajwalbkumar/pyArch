---
description: A general template to populate the Metadata for all tools in the pyArch suite.
---

# Guideline - Bundle Metadata

<pre class="language-yaml"><code class="lang-yaml"># General Guideline
# Leave 2 line spaces after every section
# Leave 1 Line Space after every line to display items in a new line

title: "Tool Title"

# context:
#   - Walls
#   - Text Notes

tooltip:   
  en_us: >-
    Version = 0.x.x
    
    Date    = DD.MM.YYYY

    ________________________________________________________________
    
    
    Description:


    This is the placeholder for a .pushbutton
    You can use it to start your pyRevit Add-In

    ________________________________________________________________
    
    
    How-To:


    1. [Hold ALT + CLICK] on the button to open its source folder.
    You will be able to override this placeholder.

    2. Automate Your Boring Work ;)

<strong>    ________________________________________________________________
</strong>    
    
    Chnagelog:
    
    
    - [DD.MM.YYYY] v1.0.0 First Update

    - [DD.MM.YYYY] v0.1.0 Beta Version - [Describe Changes]

    - [DD.MM.YYYY] v0.x.x Early Development
    
    ________________________________________________________________

# highlight: new
# highlight: updated

help_url: "https://dar-pune.gitbook.io/"

author: Full Name

# authors:
#   - John Doe
#   - Jane Doe
</code></pre>

### Useful Links

[Context Help](https://pyrevitlabs.notion.site/Bundle-Context-630fa1f3611f4ee0aa15d290275e7ef3)&#x20;

[Bundle Metadata](https://pyrevitlabs.notion.site/Bundle-Metadata-9fa4911c14fa49c48e715421400f1427)

[Versioning Format](guideline-release-versioning.md)
