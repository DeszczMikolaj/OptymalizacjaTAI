public class Main {
    public static void main(String[] args) {
        TravellingSalesmanInstanceGenerator travellingSalesmanInstanceGenerator = new TravellingSalesmanInstanceGenerator();

        TravelingSalesman travelingSalesman = new TravelingSalesman(travellingSalesmanInstanceGenerator.getInstance(50), TemperatureFunctions::staticGeometric, false);
        travelingSalesman.solve();
    }
}