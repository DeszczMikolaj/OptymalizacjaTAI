public class TemperatureFunctions {

    public static double geometric(double temperature) {
        double alpha = 0.95;
        return temperature * alpha;
    }

    public static double linear(double temperature) {
        double delta = 0.01;
        return temperature - delta;
    }

    public static double logarithmic(double temperature) {
        double beta = 0.02;

        return temperature /
                (1.0 + beta * Math.log(1.0 + temperature));
    }

    public static double exponential(double temperature) {
        double beta = 0.01;
        return temperature * Math.exp(-beta);
    }
}
