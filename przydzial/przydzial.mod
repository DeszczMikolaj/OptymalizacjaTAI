/*********************************************
 * OPL 22.1.2.0 Model
 * Author: Mikołaj
 * Creation Date: 21 mar 2026 at 22:49:03
 *********************************************/

 int dimension = ...;
 range dimensionRange = 1..dimension;
 
 int values[dimensionRange][dimensionRange] = ...;
 
 dvar boolean assigments[dimensionRange][dimensionRange];
 
 minimize sum(i in dimensionRange, j in dimensionRange) values[i][j]*assigments[i][j];
 
 subject to {
   forall(i in dimensionRange) sum(j in dimensionRange) assigments[i][j] == 1;
   forall(j in dimensionRange) sum(i in dimensionRange) assigments[i][j] == 1;
 }
 
 execute {
   	for (var i =1; i<= dimension; i++) {
   	   for (var j=1; j<=dimension; j++) {
   	     write(assigments[i][j], " ");
   	   }
   	   writeln();
   	}
 }