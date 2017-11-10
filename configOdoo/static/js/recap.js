window.onload = init;

function init(){
    
    var valid_size_btn = document.getElementById("valid_size");
    if(valid_size_btn != null){
        valid_size_btn.addEventListener("click",valid_size);   
    }
}



function valid_size(){
    
    configStr = "";
    
    var banquette = document.getElementById("banquette");
    banquetteStr = generateVariantString(banquette);
    
    var dossier = document.getElementById("dossier");
    dossierStr = generateVariantString(dossier);
    
    var rideaux = document.getElementById("rideaux");
    rideauxStr = generateVariantString(rideaux);
    
    configStr = banquetteStr + " / " + dossierStr + " / " + rideauxStr;
    
    document.getElementById("config_str").value=configStr;
    document.getElementById("valid_request").disabled = false;
}


function generateVariantString(variant){
    
    str = "";
    for(var x=0; x < variant.childNodes.length; x++){
        
        if(variant.childNodes[x].nodeName == "TD"){
            
            line = variant.childNodes[x];
            
            if(line.firstChild.className == "variant_name"){
                
                str = line.firstChild.innerHTML;
            }else if(line.firstChild.nodeName == "SPAN"){
                
                if(line.firstChild.className == "id_variant"){
                    
                    str += line.firstChild.innerHTML +" : ";
                }
            }else if(line.firstChild.name == "largeur"){
                
                str += line.firstChild.value+ " - ";
            }else if(line.firstChild.name == "longueur"){
                
                str += line.firstChild.value + " - ";
            }else if(line.firstChild.name == "epaisseur"){
                
                str += line.firstChild.value;
            }
            
        }
    }
    return str;
}