import java.util.List;

public class KnapsackNode {

    List<Item> itemsInThePath;
    Item itemInNode;
    double weightInThePath;
    double valueInThePath;
    double upperBound;

    public KnapsackNode(Item itemInTheNode, List<Item> itemsInThePath, double upperBound) {
        this.itemsInThePath = itemsInThePath;
        this.upperBound = upperBound;
    }


    public KnapsackNode(double valueInThePath, double weightInThePath, List<Item> itemsInThePath, Item itemInNode, double upperBound) {
        this.valueInThePath = valueInThePath;
        this.weightInThePath = weightInThePath;
        this.itemsInThePath = itemsInThePath;
        this.upperBound = upperBound;
        this.itemInNode = itemInNode;
    }
}
