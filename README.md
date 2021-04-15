# EBEC PROJECT GREEN TEAM

Locating trees in natural language, using open-source maps.

## Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install OSMPythonTools
```bash
pip install OSMPythonTools
```

## Details

<u>Objective 0:</u>
We use the Nominatim API to do a reverse query using the geocode. The API returns a JSON 
in wich we just select the name of the city, and the road

<u>Objective 1:</u>
A litle bit more tricky, we use the Overpass api to get all roads 
that are close to our center of interest (I) (using an extended bbox returned in the JSON of obj0).
Then, for each of them, we find the closest point (C) to the closest road to our center of interest.


The start of the segment will be the road for which the distance I-C is minimal. Cs is the associated C
The end of the segment will be the road for which the distance I-C is minimal 
AND the dot product between the vector ICs and IC is negative.


<u>Objective 2:</u>
For each tree of the list given as input, we do an orthogonal projection to the road. 
This projection is tricky because the road is not necessarly a straight line, 
but we won't go into the details.
Then we just go through the point of our road and number each tree in the order we meet their projection.

<u>Objective 3:</u>
We use the objective 1 to get the 2 roads segmenting each given point. 
We now have 4 roads and their intersection with the main road.
We go through the main road and the first intersection point that we meet corresponds to the start of our main segment.
The last one corresponds to the end of our main segment.

## Uses

For each objectives, put your entries in the if
## The Green Team

Bashir Abdel Wahed,
Loris Berniot,
Soukaina Lidam,
Paul Dufresne.
