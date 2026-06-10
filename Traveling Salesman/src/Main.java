import java.util.Map;

public class Main {
    public static void main(String[] args) {
        TravellingSalesmanInstanceGenerator travellingSalesmanInstanceGenerator = new TravellingSalesmanInstanceGenerator();

        Map<Integer, City> instance = travellingSalesmanInstanceGenerator.getInstance(20);

        double tmpInit = 100;
        for(int i=0; i<20; i++) {
            double avgSolution = 0;
            double avgIterations = 0;

            for(int j=0; j<10; j++){
                TravelingSalesman travelingSalesman = new TravelingSalesman(instance,
                        TemperatureFunctions::exponential, tmpInit, 0.3, 0.6, 1);

                Solution solution = travelingSalesman.solve();
                avgSolution += solution.distance();
                avgIterations += solution.iterations();
            }

            System.out.println("Avg solution for initTmp:" + tmpInit + " distance: "+avgSolution/10 + " iterations: " + avgIterations/10);
            tmpInit+=50;
        }


//        TravelingSalesman travelingSalesman = new TravelingSalesman(instance,
//                TemperatureFunctions::linear, 50.0, 0.3, 0.6, 1);
//
//        travelingSalesman.solve();
    }
}