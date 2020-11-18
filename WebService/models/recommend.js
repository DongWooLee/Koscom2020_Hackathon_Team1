
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('recommend', {
      stockNumber: {
        type: DataTypes.CHAR(6),
        allowNull: false,
      },
      stockName: {
        type: DataTypes.STRING(30),
        allowNull: false
      },
      stockPrice: {
        type: DataTypes.INTEGER(50),
        allowNull: false
      },
      stockPercent:{
        type: DataTypes.INTEGER(10),
        allowNull: true,
        defaultValue: 100
      },
      marketCode: {
        type: DataTypes.STRING(10),
        allowNull: false
      },
      currentPrice: {
        type: DataTypes.INTEGER(50)
      },
      createdAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: sequelize.literal('now()'),
      }
    }, {
      timestamps: false,
    });
  };