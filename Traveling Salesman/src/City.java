import java.util.HashMap;
import java.util.Map;

public class City {
    private int id;
    private final Map<Integer, Integer> idToDistance = new HashMap<>();

    public City(int id) {
        this.id = id;
    }

    public void updateCityMap(Integer idOfTargetCity, Integer distance) {
        idToDistance.put(idOfTargetCity, distance);
    }

    public Integer getDistance(Integer idOfDestinationCity) {
        return idToDistance.get(idOfDestinationCity);
    }

    public int getId() {
        return id;
    }
}
