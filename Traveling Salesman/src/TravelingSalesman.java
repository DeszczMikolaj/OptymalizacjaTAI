import java.util.*;
import java.util.function.Function;

public class TravelingSalesman {
    private RandomNumberGenerator randomNumberGenerator = new RandomNumberGenerator(120L);
    private Map<Integer, City> cities;
    private int indexRange;
    private List<CityInPath> bestOrder = new LinkedList<>();
    private int shortestPath;

    private List<CityInPath> currentPath;
    private int currentPathLength;

    private int iteration = 0;
    private int iterationStop = 1000000;
    private final int  initialTmp = 100;
    private final double  alpha = 0.1;

    private final Function<Double, Double> temperatureFunction;
    private final int iterationsPerTmpChange;
    private boolean progressCoefficientOn;

    public TravelingSalesman(Map<Integer, City> cities, Function<Double, Double> temperatureFunction, Boolean progressCoefficientOn) {
        this.cities = cities;
        indexRange = cities.size()-1;
        this.temperatureFunction = temperatureFunction;
        this.iterationsPerTmpChange = cities.size() * 20;
        this.progressCoefficientOn = progressCoefficientOn;
        generateRandomFirstSolution();

    }

    private void generateRandomFirstSolution() {
        currentPath = new LinkedList<>();
        List<City> citiesColl = cities.values().stream().toList();
        currentPathLength = 0;
        for(int i=0; i<indexRange; i++) {
            City currentCity = citiesColl.get(i);
            currentPath.add(new CityInPath(currentCity, currentPathLength));
            City nextCity = citiesColl.get(i+1);
            int distance = currentCity.getDistance(nextCity.getId());
            currentPathLength += distance;
        }
        currentPath.add(new CityInPath(citiesColl.get(indexRange), currentPathLength));

        int fromLastCityToStart = citiesColl.get(indexRange).getDistance(citiesColl.getFirst().getId());
        currentPathLength += fromLastCityToStart;

        shortestPath = currentPathLength;
    }


    public void solve() {
        iteration = 0;
        int temperatureChangeIterator = 0;
        double temperature = initialTmp * temperatureFunction.apply((double) (iteration+1) / (double) iterationStop);
        while(iteration < iterationStop) {
            if(temperatureChangeIterator == iterationsPerTmpChange) {
                if(progressCoefficientOn) {
                    temperature = initialTmp * temperatureFunction.apply((double) (iteration+1) / (double) iterationStop);
                }
                else temperature = temperature * temperatureFunction.apply((double) (iteration+1) / (double) iterationStop);
                temperatureChangeIterator = 0;
            }
            // Generating the indexes of connecting cities
            int randomCityIndexA = randomNumberGenerator.nextInt(0, indexRange);
            int randomCityIndexB = randomCityIndexA;

            while (randomCityIndexA == randomCityIndexB) {
                randomCityIndexB = randomNumberGenerator.nextInt(0, indexRange);
            }

            if(randomCityIndexA > randomCityIndexB) {
                var tmp = randomCityIndexB;
                randomCityIndexB = randomCityIndexA;
                randomCityIndexA = tmp;
            }

            // Distance from the start is stored in each node
            CityInPath selectedCityInPathA = currentPath.get(randomCityIndexA);
            City selectedCityA = selectedCityInPathA.getCity();
            int distanceToCityA =  selectedCityInPathA.getDistanceFromStart();

            CityInPath selectedCityInPathB = currentPath.get(randomCityIndexB);
            City selectedCityB = selectedCityInPathB.getCity();

            int distanceFromCityAfterBToLast = 0;
            // If the selected city is the last or one before that there is no old route left
            if(randomCityIndexB + 1 < indexRange) {
                //
                distanceFromCityAfterBToLast  = currentPath.getLast().getDistanceFromStart() - currentPath.get(randomCityIndexB + 1).getDistanceFromStart();
            }

            //Copying unchanged part of the path
            List<CityInPath> fromStartToA = new LinkedList<>(currentPath.subList(0, randomCityIndexA+1));
            List<CityInPath> tmpCityInPath = new LinkedList<>(fromStartToA);

            //Calculating the distance in reversed order
            // First rewire
            int distanceFromAToB =  selectedCityA.getDistance(selectedCityB.getId());
            tmpCityInPath.add(new CityInPath(selectedCityB, selectedCityInPathA.getDistanceFromStart() + distanceFromAToB));
            int distanceInReversedOrder = distanceFromAToB;

            // Reversed order
            for(int i = randomCityIndexB; i>randomCityIndexA + 1; i--) {
               City currentCity = currentPath.get(i).getCity();
               City nextCity =  currentPath.get(i-1).getCity();
               int distance = currentCity.getDistance(nextCity.getId());
               distanceInReversedOrder+=distance;

               // constructing candidate for a new path
               int distanceFromStart = tmpCityInPath.getLast().getDistanceFromStart();
               tmpCityInPath.add(new CityInPath(nextCity,distanceFromStart + distance ));
            }
            // Second rewire, happens if the selected node wasn't the last
            int distanceFromLastCityToFirst;
            if(randomCityIndexB != indexRange) {

                City lastCityInReversedOrder = currentPath.get(randomCityIndexA +1).getCity();
                City nextCity = currentPath.get(randomCityIndexB+1).getCity();
                int distance = lastCityInReversedOrder.getDistance(nextCity.getId());
                distanceInReversedOrder += distance;

                int distanceFromStart = tmpCityInPath.getLast().getDistanceFromStart();
                tmpCityInPath.add(new CityInPath(nextCity,distanceFromStart + distance ));
                // When the selected city wasn't "last" then that part doesn't change
                City firstCity = currentPath.getFirst().getCity();
                City lastCity = currentPath.getLast().getCity();
                distanceFromLastCityToFirst = lastCity.getDistance(firstCity.getId());
            }
            // When the selected city was "last" then the last reversed node points to the start
            else {
                City firstCity = tmpCityInPath.getFirst().getCity();
                City lastCity = tmpCityInPath.getLast().getCity();
                distanceFromLastCityToFirst = lastCity.getDistance(firstCity.getId());
            }


            int newDistance = distanceToCityA + distanceInReversedOrder + distanceFromCityAfterBToLast + distanceFromLastCityToFirst;

            int delta = newDistance - currentPathLength;

            System.out.println("Threshold: " + Math.exp(-delta / temperature) + " delta: " + delta);
            if(delta < 0 || Math.exp(-delta / temperature) >= Math.random()) {
                // When the new solution is selected we need to reconstruct the path fully and update distances
                //Copying unchanged part after selected City B

                if(randomCityIndexB + 2 <= indexRange) {
                    List<CityInPath> fromTwoAfterBToEnd = new LinkedList<>(currentPath.subList(randomCityIndexB+2, indexRange+1));
                    fromTwoAfterBToEnd.forEach(cityInPath -> cityInPath.changeDistanceFromStartBy(delta));
                    tmpCityInPath.addAll(fromTwoAfterBToEnd);
                }

                currentPath = tmpCityInPath;
                currentPathLength = newDistance;

                if(currentPathLength < shortestPath ) {
                    shortestPath = newDistance;
                    bestOrder = currentPath;
                }

                if (newDistance != calculateDistanceTEST(tmpCityInPath)) {
                    //System.out.println("Distance mismatch, iteration " + iteration);
                    return;
                }
                System.out.println(currentPathLength + " tmp: "+ temperature);
            }


            iteration++;
            temperatureChangeIterator++;
        }
        System.out.println(shortestPath);
    }


    private int calculateDistanceTEST(List<CityInPath> tmpCityInPath) {
        int distance = 0;

        for(int i=0;i<indexRange;i++) {
            City city = tmpCityInPath.get(i).getCity();
            City nextCity = tmpCityInPath.get(i+1).getCity();
            distance += city.getDistance(nextCity.getId());
        }
        City city = tmpCityInPath.getLast().getCity();
        City nextCity = tmpCityInPath.getFirst().getCity();
        distance += city.getDistance(nextCity.getId());

        return distance;
    }
}
