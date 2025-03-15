function generateFakeSalesData() {
    const salesData = {
        yearlySales: [],
        monthlySales: [],
        weeklySales: [],
        dailySales: [],
        topBooks: [],
        totalSales: 0, // Initialize totalSales to 0
        totalRevenue: 0 // Initialize totalRevenue to 0
    };

    // Generate fake yearly sales data
    for (let i = 1; i <= 5; i++) {
        const sales = 1200; // Set sales to 1200
        salesData.yearlySales.push({ year: `Year ${i}`, sales });
        salesData.totalSales += sales;
        salesData.totalRevenue += sales * 20; // Assume each sale is $20
    }

    // Generate fake monthly sales data
    for (let i = 1; i <= 12; i++) {
        const sales = 100; // Set sales to 100
        salesData.monthlySales.push({ month: `Month ${i}`, sales });
        salesData.totalSales += sales;
        salesData.totalRevenue += sales * 20; // Assume each sale is $20
    }

    // Generate fake weekly sales data
    for (let i = 1; i <= 52; i++) {
        const sales = 25; // Set sales to 25
        salesData.weeklySales.push({ week: `Week ${i}`, sales });
        salesData.totalSales += sales;
        salesData.totalRevenue += sales * 20; // Assume each sale is $20
    }

    // Generate fake daily sales data
    for (let i = 1; i <= 365; i++) {
        const sales = 3; // Set sales to 3
        salesData.dailySales.push({ day: `Day ${i}`, sales });
        salesData.totalSales += sales;
        salesData.totalRevenue += sales * 20; // Assume each sale is $20
    }

    // Generate fake top selling books data
    for (let i = 1; i <= 5; i++) {
        salesData.topBooks.push({
            title: `Book ${i}`,
            sales: 100 // Set sales to 100
        });
    }

    return salesData;
}

// Export the function for use in other files
export { generateFakeSalesData };
