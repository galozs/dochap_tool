function fix_ids(){
    var groups = document.getElementsByClassName("transcript_id_rect");
    var svg_drawings = document.getElementsByTagName("svg");
    var bbBox = null;
    if (svg_drawings){
        bbBox = svg_drawings[0].getBBox();
    }
    var minX = 2;
    var rectOffset = 2;
    fix_rect_and_text(groups, bbBox, minX, rectOffset);
}


function fix_status(){
    var groups = document.getElementsByClassName("match_status_group");
    var svg_drawings = document.getElementsByTagName("svg");
    var bbBox = null;
    if (svg_drawings){
        bbBox = svg_drawings[0].getBBox();
    }
    var minX = 2;
    var rectOffset = 2;
    fix_rect_and_text(groups, bbBox, minX, rectOffset);
}



function fix_rect_and_text(groups, bbBox, minX, rectOffset){
    var script_fixed_class_name = 'script_fixed';
    for (var i=0; i<groups.length; i++){
        var should_fix = !groups[i].classList.contains(script_fixed_class_name);
        if (!should_fix){
            continue;
        }
        var rect = groups[i].getElementsByTagName("rect")[0];
        var text = groups[i].getElementsByTagName("text")[0];
        var textBoundingBox = text.getBBox();
        var diff = bbBox.width - textBoundingBox.x - textBoundingBox.width - rectOffset - minX;
        var new_x = textBoundingBox.x - rectOffset;
        var spans = text.getElementsByTagName('tspan');
        if (diff < 0){
            new_x = textBoundingBox.x + diff;
            for (var j=0; j<spans.length; j++){
                spans[j].setAttribute('x', new_x + rectOffset);
            }
        }
        else if(new_x < minX){
            new_x = minX
            for (var j=0; j<spans.length; j++){
                spans[j].setAttribute('x', new_x + rectOffset);
            }
        }
        text.setAttribute('x', new_x + rectOffset);
        textBoundingBox = text.getBBox();
        rect.setAttribute('x', textBoundingBox.x - rectOffset);
        rect.setAttribute('y', textBoundingBox.y - rectOffset);
        rect.setAttribute('width', textBoundingBox.width + (2* rectOffset));
        rect.setAttribute('height', textBoundingBox.height + (2* rectOffset));
        groups[i].classList.add(script_fixed_class_name);
    }

}

function fix_tooltips(){
    var groups = document.getElementsByClassName("special_rect_tooltip");
    var svg_drawings = document.getElementsByTagName("svg");
    var bbBox = null;
    if (svg_drawings){
        bbBox = svg_drawings[0].getBBox();
    }
    var minX = 6;
    var rectOffset = 4;
    fix_rect_and_text(groups, bbBox, minX, rectOffset);
}

function fix_all(){
    fix_tooltips();
    fix_status();
    fix_ids();
}
window.onload = fix_all;

