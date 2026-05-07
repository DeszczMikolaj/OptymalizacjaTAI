import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;

public class KnapsackTest {

    public static void main(String[] args) {
       // runStaticTests();
       runGeneratedTest();
    }

    private static void runGeneratedTest() {
        for(int i = 5; i < 100; i += 10){
            KnapsackProblemInstance instance = KnapsackProblemInstanceGenerator.generateInstance(i);

            long start = System.nanoTime();

            KnapsackBnB solver = new KnapsackBnB(instance.items(), instance.weightLimit(), true, true, 0.5);
            List<Item> solutionItems = solver.runKnapsackBnBTask();

            long end = System.nanoTime();

            long elapsedNanos = end - start;
            double elapsedMillis = elapsedNanos / 1_000_000.0;

            System.out.println("================================");
            System.out.println("For " + i + " items: " + elapsedMillis + " ms of execution time");

            double solutionValue = 0;
            for(Item item: solutionItems) {
                solutionValue += item.value();
            }
            System.out.println("Weight limit: " + instance.weightLimit() + " ||| Value obtained: " + solutionValue);
        }
    }


    private static void runStaticTest(
            String testName,
            List<Item> items,
            double capacity,
            double expected
    ) {

        KnapsackBnB solver = new KnapsackBnB(new ArrayList<>(items), capacity);
        List<Item> actualItems = solver.runKnapsackBnBTask();
        double actualValue = 0;
        for(Item item: actualItems) {
            actualValue += item.value();
        }

        boolean passed = Math.abs(actualValue - expected) < 0.0001;

        System.out.println("================================");
        System.out.println(testName);
        System.out.println("Expected: " + expected);
        System.out.println("Actual:   " + actualValue);
        System.out.println("Result:   " + (passed ? "PASSED" : "FAILED"));
    }

    private static void runStaticTests() {
        runStaticTest(
                "Classic Test",
                KnapsackTestData.knownOptimalSet(),
                50,
                380
        );

        runStaticTest(
                "Classic Test",
                KnapsackTestData.classicSet(),
                50,
                220
        );

        runStaticTest(
                "Small Set",
                KnapsackTestData.smallSet(),
                30,
                160
        );

        runStaticTest(
                "Equal Ratio",
                KnapsackTestData.equalRatioSet(),
                10,
                50
        );

        runStaticTest(
                "Heavy Items",
                KnapsackTestData.heavyItemsSet(),
                50,
                300
        );

        runStaticTest(
                "Single Item Fits",
                KnapsackTestData.singleItemFits(),
                20,
                50
        );

        runStaticTest(
                "Single Item Too Heavy",
                KnapsackTestData.singleItemTooHeavy(),
                20,
                0
        );

        runStaticTest(
                "Empty Set",
                KnapsackTestData.emptySet(),
                100,
                0
        );

        runStaticTest(
                "Medium Set",
                KnapsackTestData.mediumSet(),
                50,
                107
        );
    }
}