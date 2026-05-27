import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class TravellingSalesmanInstanceGenerator {
    private final RandomNumberGenerator randomNumberGenerator = new RandomNumberGenerator(300L);

    public Map<Integer, City> getInstance(int numberOfCities){
        Map<Integer, City> generatedCities = new HashMap<>();

        for(int i=0; i<numberOfCities; i++) {
            City city = new City(i);
            for(int j=0; j<numberOfCities; j++) {
                if(i==j) continue;
                Integer distance = randomNumberGenerator.nextInt(1,100);
                city.updateCityMap(j, distance);
            }
            generatedCities.put(i, city);
        }
        return generatedCities;
    }
}
