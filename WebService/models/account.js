/*
create table account(
  accountId integer(50) not null auto_increment primary key,
  userId varchar(50),
  bankId integer(50),
  balance integer(50),
  foreign key(userId) references user(userId),
  foreign key(bankId) references bank(bankId)
);
*/
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('account', {
      accountId: {
        type: DataTypes.INTEGER(50),
        allowNull: false,
        unique: true,
        autoIncrement:true,
        primaryKey: true
      },/*
      userId: {
        type: DataTypes.STRING(50),
      },
      */
      bankName: {
        type: DataTypes.STRING(30),
        allowNull: false
      },
      balance: {
        type: DataTypes.INTEGER(50),
      },
    }, {
      timestamps: false,
    });
  };