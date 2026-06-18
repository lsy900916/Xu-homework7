/*
 Target Server Type    : SQL Server
*/


-- ----------------------------
-- Table structure for batch_counter
-- ----------------------------
IF EXISTS (SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID(N'[dbo].[batch_counter]') AND type IN ('U'))
	DROP TABLE [dbo].[batch_counter]
GO

CREATE TABLE [dbo].[batch_counter] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [batch_date] date  NOT NULL,
  [seq] int DEFAULT ((1)) NOT NULL
)
GO


-- ----------------------------
-- Records of batch_counter
-- ----------------------------
SET IDENTITY_INSERT [dbo].[batch_counter] ON
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'21', N'2026-04-08', N'11')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'22', N'2026-04-09', N'4')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'23', N'2026-04-10', N'2')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'24', N'2026-04-14', N'2')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'25', N'2026-04-15', N'4')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'26', N'2026-04-16', N'8')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'27', N'2026-04-17', N'7')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'28', N'2026-04-18', N'3')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'29', N'2026-04-21', N'1')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'30', N'2026-04-22', N'5')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'31', N'2026-04-23', N'3')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'32', N'2026-04-24', N'4')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'33', N'2026-04-25', N'1')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'34', N'2026-04-27', N'1')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'35', N'2026-04-28', N'1')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'36', N'2026-05-01', N'6')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'37', N'2026-05-02', N'15')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'38', N'2026-05-03', N'8')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'39', N'2026-05-04', N'11')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'40', N'2026-05-05', N'7')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'41', N'2026-05-07', N'4')
GO

INSERT INTO [dbo].[batch_counter] ([id], [batch_date], [seq]) VALUES (N'45', N'2026-05-08', N'5')
GO

SET IDENTITY_INSERT [dbo].[batch_counter] OFF
GO


-- ----------------------------
-- Uniques structure for table batch_counter
-- ----------------------------
ALTER TABLE [dbo].[batch_counter] ADD CONSTRAINT [uk_batch_date] UNIQUE NONCLUSTERED ([batch_date] ASC)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
GO


-- ----------------------------
-- Primary Key structure for table batch_counter
-- ----------------------------
ALTER TABLE [dbo].[batch_counter] ADD CONSTRAINT [PK__batch_co__3213E83F28EF28ED] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
GO

