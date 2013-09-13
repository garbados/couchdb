## Licensed under the Apache License, Version 2.0 (the "License"); you may not
## use this file except in compliance with the License. You may obtain a copy of
## the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations under
## the License.

import sys, os

extensions = ["sphinx.ext.todo", "sphinx.ext.extlinks"]

source_suffix = ".rst"

master_doc = "index"

nitpicky = True

release = "1.0.2"

project = u"Cloudant Documentation"

copyright = u"2013 Cloudant"

highlight_language = "json"

pygments_style = "sphinx"

html_theme = "basic"

templates_path = ["../templates"]

html_static_path = ["../static"]

html_title = "Cloudant Documentation"

html_style = "cloudant_rtd.css"

html_logo = "../images/logo.png"

html_favicon = "../images/favicon.ico"

html_sidebars= {
    "**": [
        "searchbox.html",
        "localtoc.html",
#        "relations.html",
        "help.html",
    ]
}

text_newlines = "native"

latex_documents = [(
    "index",
    "Cloudant-API-Reference.tex",
    "Documentation",
    "",
    "manual",
    True
)]

latex_logo = "../images/CloudantLogo_RGB_2C-noRightMargin.png"

latex_elements = {
    "papersize":"a4paper"
}

texinfo_documents = [(
    "index",
    "Cloudant",
    project,
    "",
    "Cloudant",
    "Cloudant",
    "Databases",
    True
)]

extlinks = {
}