/*
create table user(
  userId varchar(50) not null primary key,
  name varchar(30) not null,
  password varchar(50) not null,
  transferDate DATE,
  transferAmount integer(30),
  transferPeriod integer(10)
);

*/
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('user', {
        userId: {
            type: DataTypes.STRING(50),
            allowNull: false,
            unique: true,
        },
        telegramId: {
            type: DataTypes.STRING(50),
            allowNull: true,
        },
        name: {
            type: DataTypes.STRING(30),
            allowNull: false,
        },
        password: {
            type: DataTypes.STRING(50),
            allowNull: false,
        },
        transferDate: {
            type: DataTypes.STRING(20),
        },
        transferAmount: {
            type: DataTypes.INTEGER(10),
            defaultValue: 1
        },
        transferPeriod: {
            type: DataTypes.INTEGER(10),
            defaultValue: 1
        },
        expectedProfits:{
            type: DataTypes.INTEGER(3),
            defaultValue: 2
        }
        }, {
        timestamps: false,
    });
  };