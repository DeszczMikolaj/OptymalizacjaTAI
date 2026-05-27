public class TemperatureFunctions {

    public static double staticGeometric(double progressCoefficient) {
        return 0.95;
    }

    public static double linear(double progressCoefficient) {
        return 1.0 - progressCoefficient;
    }

    public static double logarithmic(double progressCoefficient) {
        // Increase to slow down cooling, never zero tmp
        double scalingCoefficient = 40;
        return 1.0 / (Math.log( 1+ progressCoefficient * scalingCoefficient));
    }

    public static double exponential(double progressCoefficient) {
        // Increase to slow down cooling, fast decrease, plato near 0
        double scalingCoefficient = 0.01;
        return Math.pow(scalingCoefficient, progressCoefficient);
    }
}
