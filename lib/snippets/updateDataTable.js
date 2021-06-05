var data = source.data;
var idx = data["index"].length;
var selection = cb_obj.value;
var obj = obj;

console.log("selected country: " + selection);
//var orig = JSON.parse(JSON.stringify(source.data));

console.log("used data");
console.log(source.data);
console.log("original data:");
console.log(orig.data);

var filtered = {};
for (var key in data) {
  filtered[key] = [];
}

// set vars from data table keys
var {
  "Province/State": states,
  "Country/Region": countries,
  Lat: lats,
  Long: lons,
  Date: dates,
  Confirmed: confirmeds,
  Deaths: deaths,
  Recovered: recovereds,
  Active: actives,
  "WHO Region": whos,
} = data;

for (var i = 0; i < idx; i++) {
  // validate country if all is selected show original data source
  if (selection == "all") {
    //source.data = orig;
    break;
  }
  if (countries[i] == selection) {
    //console.log('located selection at row index ' + i + ' with value ' + countries[i]);
    // for each key in original array
    for (var key in data) {
      //push original values to new key arrays
      filtered[key].push(data[key][i]);
    }
  }
}

//try updating source with filtered data, check if selection is all
if (selection != "all") {
  source.data = filtered;
} else {
  source.data = orig.data;
}

console.log(source.data);
console.log("original after changes");
console.log(orig.data);
source.change.emit();
obj.change.emit();
