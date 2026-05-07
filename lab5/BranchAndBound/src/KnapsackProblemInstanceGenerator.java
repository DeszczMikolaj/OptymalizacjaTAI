import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class KnapsackProblemInstanceGenerator {

    static RandomNumberGenerator randomNumberGenerator;

    static KnapsackProblemInstance generateInstance(int numberOfItems, int seedValue) {
        randomNumberGenerator = new RandomNumberGenerator(seedValue);
        List<Item> items = new ArrayList<>();
        double weightSum = 0;
        for(int i = 0; i< numberOfItems; i++) {
            double value =  randomNumberGenerator.nextInt(1,10);
            double weight = randomNumberGenerator.nextInt(1,10);
            items.add(new Item(value, weight));
            weightSum += weight;
        }
        double weightLimit = randomNumberGenerator.nextInt((int) Math.floor(weightSum/4), (int) Math.floor(weightSum/2));
        return new KnapsackProblemInstance(items, weightLimit);
    }

    static KnapsackProblemInstance generateInstance(int numberOfItems) {
        return generateInstance(numberOfItems, 1200);
    }
}
