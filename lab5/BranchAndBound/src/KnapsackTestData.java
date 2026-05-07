import java.util.List;

public class KnapsackTestData {

    // Simple optimal pick: items 0 + 1 = value 160
    public static List<Item> smallSet() {
        return List.of(
                new Item(100, 20),
                new Item(60, 10),
                new Item(120, 30)
        );
    }

    // Classic knapsack example
    public static List<Item> classicSet() {
        return List.of(
                new Item(60, 10),
                new Item(100, 20),
                new Item(120, 30)
        );
    }

    // Items with equal ratios
    public static List<Item> equalRatioSet() {
        return List.of(
                new Item(10, 2),
                new Item(20, 4),
                new Item(30, 6),
                new Item(40, 8)
        );
    }

    // Large weight edge case
    public static List<Item> heavyItemsSet() {
        return List.of(
                new Item(500, 100),
                new Item(400, 90),
                new Item(200, 30),
                new Item(300, 50)
        );
    }

    // Single item fits
    public static List<Item> singleItemFits() {
        return List.of(
                new Item(50, 10)
        );
    }

    // Single item too heavy
    public static List<Item> singleItemTooHeavy() {
        return List.of(
                new Item(50, 100)
        );
    }

    // Empty set
    public static List<Item> emptySet() {
        return List.of();
    }

    // More realistic random set
    public static List<Item> mediumSet() {
        return List.of(
                new Item(70, 31),
                new Item(20, 10),
                new Item(39, 20),
                new Item(37, 19),
                new Item(7, 4),
                new Item(5, 3),
                new Item(10, 6)
        );
    }

    public static List<Item> knownOptimalSet() {

        return List.of(

                new Item(100, 10), // optimal
                new Item(280, 40), // optimal

                new Item(120, 24),
                new Item(120, 24),
                new Item(150, 30),
                new Item(200, 41),
                new Item(90, 20),
                new Item(60, 10),
                new Item(40, 9),
                new Item(30, 5),

                // filler items
                new Item(75, 18),
                new Item(110, 26),
                new Item(95, 21),
                new Item(130, 28),
                new Item(170, 37),
                new Item(80, 16),
                new Item(45, 11),
                new Item(55, 13),
                new Item(65, 14),
                new Item(140, 32),

                new Item(20, 6),
                new Item(25, 7),
                new Item(35, 8),
                new Item(85, 19),
                new Item(115, 27),
                new Item(125, 29),
                new Item(135, 31),
                new Item(145, 33),
                new Item(155, 35),
                new Item(165, 36),

                new Item(175, 38),
                new Item(185, 39),
                new Item(195, 42),
                new Item(205, 43),
                new Item(215, 44),
                new Item(225, 45),
                new Item(235, 46),
                new Item(245, 47),
                new Item(255, 48),
                new Item(265, 49),

                new Item(15, 4),
                new Item(18, 5),
                new Item(22, 6),
                new Item(28, 7),
                new Item(32, 8),
                new Item(38, 9),
                new Item(42, 10),
                new Item(48, 11),
                new Item(52, 12),
                new Item(58, 13),

                new Item(62, 14),
                new Item(68, 15),
                new Item(72, 16),
                new Item(78, 17),
                new Item(82, 18),
                new Item(88, 19),
                new Item(92, 20),
                new Item(98, 21),
                new Item(102, 22),
                new Item(108, 23),

                new Item(112, 24),
                new Item(118, 25),
                new Item(122, 26),
                new Item(128, 27),
                new Item(132, 28),
                new Item(138, 29),
                new Item(142, 30),
                new Item(148, 31),
                new Item(152, 32),
                new Item(158, 33),

                new Item(162, 34),
                new Item(168, 35),
                new Item(172, 36),
                new Item(178, 37),
                new Item(182, 38),
                new Item(188, 39),
                new Item(192, 40),
                new Item(198, 41),
                new Item(202, 42),
                new Item(208, 43),

                new Item(212, 44),
                new Item(218, 45),
                new Item(222, 46),
                new Item(228, 47),
                new Item(232, 48),
                new Item(238, 49),
                new Item(242, 50),
                new Item(248, 51),
                new Item(252, 52),
                new Item(258, 53),

                new Item(262, 54),
                new Item(268, 55),
                new Item(272, 56),
                new Item(278, 57),
                new Item(282, 58),
                new Item(288, 59),
                new Item(292, 60),
                new Item(298, 61)
        );
    }
}