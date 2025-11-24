from __future__ import annotations

from st_aggrid import JsCode

# Styles

bold_text = "font-weight : bold"


risk_menu = {

    "container" : {"background-color" : "##d7cafc"},
    "icon": { "font-size" : "20spx" },
    "nav-link" : {

        "font-size" : "12px",
        "margin" : "0px",
        "font-weight" : "normal"

    },
    "nav-link-selected" : {

        "background-color" : "#7645ff",
        "font-weight" : "normal"

    }

}


screeners_custom_css = {

    ".ag-root-wrapper": {"border": "1"},
    ".ag-body-viewport": {"overflow-x": "auto !important"},
    ".ag-body-horizontal-scroll-viewport": {"overflow-x": "auto !important"},

}


screeners_js_code = JsCode(
    
    """
    function(params){
        setTimeout(function(){
            var ids = [];
            params.columnApi.getAllColumns().forEach(function(c){ ids.push(c.getColId()); });
            // Size to content (headers included = false -> include headers in calc)
            params.columnApi.autoSizeColumns(ids, false);
            // If everything fits and you STILL want a scrollbar, you could set minWidth on some columns
            // params.api.refreshCells({force: true});
        }, 50);
    }
    """
    )