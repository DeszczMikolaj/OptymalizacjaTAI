import java.util.*;

public class KnapsackBnB {


    private boolean beanSearchBoundsAdjustment = false;
    private double beanSearchBoundsAdjustmentFactor = 0.2;

    private boolean beanSearchExploreBest = false;
    private double beanSearchExploreBestFactor = 0.5;


    private double lowerBoundValue = 0;

    private List<Item> lowerBoundSolution = new ArrayList<>();

    private List<Item> itemsSorted;

    private double knapsackWeightLimit;

    final private PriorityQueue<KnapsackNode>  queue = priorityQueueOrderedDescByUpperBound();

    private static PriorityQueue<KnapsackNode> priorityQueueOrderedDescByUpperBound() {
        return new PriorityQueue<>((nodeA, nodeB) -> Double.compare(nodeB.upperBound ,nodeA.upperBound));
    }

    public KnapsackBnB(List<Item> itemsSet, Double knapsackWeightLimit) {
        this (itemsSet, knapsackWeightLimit, false);
    }

    public KnapsackBnB(List<Item> itemsSet, Double knapsackWeightLimit, Boolean enableBeanSearchBoundsAdjustment) {
        this.itemsSorted = sortItemsDescByValuePerWeightUnit(itemsSet);
        this.knapsackWeightLimit = knapsackWeightLimit;
        queue.add(new KnapsackNode(0.0,0.0, List.of(), null, 0.0));
        this.beanSearchBoundsAdjustment = enableBeanSearchBoundsAdjustment;
        initializeLowerBound();
    }

    public KnapsackBnB(List<Item> itemsSet, Double knapsackWeightLimit, Boolean beanSearchExploreBest, double exploreBestFactor) {
        this.itemsSorted = sortItemsDescByValuePerWeightUnit(itemsSet);
        this.knapsackWeightLimit = knapsackWeightLimit;
        queue.add(new KnapsackNode(0.0,0.0, List.of(), null, 0.0));
        this.beanSearchExploreBest = beanSearchExploreBest;
        beanSearchExploreBestFactor = exploreBestFactor;
        initializeLowerBound();
    }

    public KnapsackBnB(List<Item> itemsSet, Double knapsackWeightLimit, Boolean enableBeanSearchBoundsAdjustment,  Boolean beanSearchExploreBest, double exploreBestFactor) {
        this.itemsSorted = sortItemsDescByValuePerWeightUnit(itemsSet);
        this.knapsackWeightLimit = knapsackWeightLimit;
        queue.add(new KnapsackNode(0.0,0.0, List.of(), null, 0.0));
        this.beanSearchBoundsAdjustment = enableBeanSearchBoundsAdjustment;
        this.beanSearchExploreBest = beanSearchExploreBest;
        beanSearchExploreBestFactor = exploreBestFactor;
        initializeLowerBound();
    }

    private void initializeLowerBound() {
        for (Item item : itemsSorted) {
            if (lowerBoundValue + item.weight() <= knapsackWeightLimit) {
                lowerBoundValue += item.value();
                lowerBoundSolution.add(item);
            } else break;
        }
        if(beanSearchBoundsAdjustment) lowerBoundValue = lowerBoundValue * (1.0 + beanSearchBoundsAdjustmentFactor);
    }

    private static List<Item> sortItemsDescByValuePerWeightUnit(List<Item> itemsSet) {
        return itemsSet.stream().sorted((itemA, itemB) -> Double.compare(itemB.value() / itemB.weight(), itemA.value() / itemA.weight())).toList();
    }

    public List<Item> runKnapsackBnBTask() {
        while (!queue.isEmpty()) {
            KnapsackNode currentNode = queue.poll();
            double currentWeight = currentNode.weightInThePath;
            double currentValue = currentNode.valueInThePath;
            List<Item> nonUsedItems =  itemsSorted.stream().filter(item -> !currentNode.itemsInThePath.contains(item)).toList();

            if(currentValue > lowerBoundValue) {
                lowerBoundValue = currentValue;
                lowerBoundSolution = currentNode.itemsInThePath;
            }

            // To avoid duplication.
            int currentNodeGlobalIndex = -1;
            if(currentNode.itemInNode != null) currentNodeGlobalIndex = itemsSorted.indexOf(currentNode.itemInNode);

            List<KnapsackNode> exploreBestTempList = new ArrayList<>();

            for(Item item: nonUsedItems) {
                if(itemsSorted.indexOf(item) < currentNodeGlobalIndex) continue;

                if(currentWeight + item.weight() <= knapsackWeightLimit) {
                    double upperBound = calculateUpperBoundForNewNode(currentNode, item, new ArrayList<>(nonUsedItems));
                    if(upperBound > lowerBoundValue) {
                        List<Item> itemsForNewPath =  new ArrayList<>(currentNode.itemsInThePath);
                        itemsForNewPath.add(item);
                        KnapsackNode newNode = new KnapsackNode(currentValue + item.value(), currentWeight + item.weight(),itemsForNewPath, item, upperBound);
                        if(!beanSearchExploreBest) {
                            queue.add(newNode);
                        }
                        else exploreBestTempList.add(newNode);
                    }
                }
            }
            if(beanSearchExploreBest) {
                exploreBestTempList.sort((nodeA, nodeB) -> Double.compare(nodeB.upperBound, nodeA.upperBound));
                int numberOfObjectsToExplore = (int) (exploreBestTempList.size() * beanSearchExploreBestFactor);
                Iterator<KnapsackNode> iterator = exploreBestTempList.iterator();
                while(numberOfObjectsToExplore > 0 && iterator.hasNext()) {
                    queue.add(iterator.next());
                    numberOfObjectsToExplore--;
                }
            }
        }
        return lowerBoundSolution;
    }

    private double calculateUpperBoundForNewNode(KnapsackNode currentNode, Item itemForNewNode, List<Item> nonUsedItems) {
        nonUsedItems.remove(itemForNewNode);
        double currentValue = currentNode.valueInThePath + itemForNewNode.value();
        double currentWeight = currentNode.weightInThePath + itemForNewNode.weight();

        double estimatedValueWithRelaxedBoundaries = currentValue;

        double currentNodeGlobalIndex = itemsSorted.indexOf(currentNode.itemInNode);
        // nonUsedItems is already sorted
        for(Item item: nonUsedItems) {
            if(itemsSorted.indexOf(item) < currentNodeGlobalIndex) continue;
            double remainingWeight = knapsackWeightLimit - currentWeight;
            if(remainingWeight > item.weight()) {
                estimatedValueWithRelaxedBoundaries += item.value();
                currentWeight += item.weight();
            }
            else {
                double fraction =  remainingWeight / item.weight();
                double fractionValue = fraction * item.value();
                estimatedValueWithRelaxedBoundaries += fractionValue;
                break;
            }

        }

        if(beanSearchBoundsAdjustment) estimatedValueWithRelaxedBoundaries = estimatedValueWithRelaxedBoundaries * (1.0 - beanSearchBoundsAdjustmentFactor);

        return estimatedValueWithRelaxedBoundaries;
    }

}
