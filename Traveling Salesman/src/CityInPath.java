public class CityInPath {
    private final City city;
    private Integer distanceFromStart;

    public CityInPath(City city, Integer distanceFromStart) {
        this.city = city;
        this.distanceFromStart = distanceFromStart;
    }

    public City getCity() {
        return city;
    }

    public Integer getDistanceFromStart() {
        return distanceFromStart;
    }

    public void changeDistanceFromStartBy(Integer change) {
        distanceFromStart+=change;
    }
}
