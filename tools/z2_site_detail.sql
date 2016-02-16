/*
Navicat MySQL Data Transfer

Source Server         : Spy
Source Server Version : 50531
Source Host           : 192.168.1.31:3306
Source Database       : z2sql

Target Server Type    : MYSQL
Target Server Version : 50531
File Encoding         : 65001

Date: 2016-02-11 17:37:15
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `z2_site_detail`
-- ----------------------------
DROP TABLE IF EXISTS `z2_site_detail`;
CREATE TABLE `z2_site_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detail` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of z2_site_detail
-- ----------------------------
INSERT INTO `z2_site_detail` VALUES ('1', 'MS-DOS');
INSERT INTO `z2_site_detail` VALUES ('2', 'Windows - 16 bit');
INSERT INTO `z2_site_detail` VALUES ('3', 'Windows - 32 bit');
INSERT INTO `z2_site_detail` VALUES ('4', 'Windows - 64 bit');
INSERT INTO `z2_site_detail` VALUES ('5', 'Linux');
INSERT INTO `z2_site_detail` VALUES ('6', 'OSX');
INSERT INTO `z2_site_detail` VALUES ('7', 'Featured Game');
INSERT INTO `z2_site_detail` VALUES ('8', 'Contest');
INSERT INTO `z2_site_detail` VALUES ('9', 'Soundtrack');
INSERT INTO `z2_site_detail` VALUES ('10', 'Font');
INSERT INTO `z2_site_detail` VALUES ('11', 'Hack');
