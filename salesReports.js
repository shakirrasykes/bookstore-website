const mongoose = require('mongoose');

// Sales schema and model
const salesSchema = new mongoose.Schema({
    date: Date,
    amount: Number
});
const Sale = mongoose.model('Sale', salesSchema);

// Function to generate sales report
async function generateSalesReport(period) {
    const now = new Date();
    let startDate;

    switch (period) {
        case 'daily':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            break;
        case 'weekly':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay());
            break;
        case 'monthly':
            startDate = new Date(now.getFullYear(), now.getMonth(), 1);
            break;
        case 'yearly':
            startDate = new Date(now.getFullYear(), 0, 1);
            break;
        default:
            throw new Error('Invalid period');
    }

    const sales = await Sale.aggregate([
        { $match: { date: { $gte: startDate } } },
        { $group: { _id: null, totalSales: { $sum: '$amount' } } }
    ]);

    return sales.length > 0 ? sales[0].totalSales : 0;
}

module.exports = {
    generateSalesReport
};
