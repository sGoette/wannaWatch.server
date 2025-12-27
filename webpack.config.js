import path from "path";
import HtmlWebpackPlugin from "html-webpack-plugin";
import { CleanWebpackPlugin } from "clean-webpack-plugin";
import webpack from "webpack";

const exports = {
  entry: "./frontend/src/index.tsx",
  output: {
    filename: "[name].[contenthash].js",
    path: path.resolve("./dist/frontend"),
    publicPath: "/",
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  devtool: "source-map",
  module: {
    rules: [
      {
        test: /\.(ts|js)x?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: [
                "@babel/preset-env",
                "@babel/preset-react",
                "@babel/preset-typescript",
              ],
            },
          },
        ],
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/i,
        type: "asset/resource",
      },
    ],
  },
  plugins: [
    new CleanWebpackPlugin(),
    new HtmlWebpackPlugin({
      template: "./frontend/public/index.html",
    }),
    new webpack.DefinePlugin({
      __WSURL__: JSON.stringify('ws://localhost:4000/ws')
    })
  ],
  devServer: {
    static: "./dist/frontend",
    hot: true,
    allowedHosts: "all",
    historyApiFallback: true,
    port: 3000,
    open: true,
    proxy: [
      {
        context: ["/api"],
        target: "http://localhost:4000"
      }
    ]
  },
  mode: "development",
};

export default exports